from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.source import Source
from app.db.models.extracted_record import ExtractedRecord
from app.scraping.extractors import (
    TelecomExtractor, BankingExtractor, InsuranceExtractor,
    HospitalityExtractor, EducationExtractor, TransportExtractor, EconetExtractor
)
from app.scraping.extractors.base import BaseExtractor
from app.scraping.extractors.generic import GenericExtractor
from app.services.webhook_publisher import WebhookPublisher
from app.services.intelligence import IntelligenceService
from app.config import settings
from app.logging import logger


class ExtractorService:
    """Service for extracting normalized records from raw snapshots."""

    def __init__(self, db: Session):
        self.db = db

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def extract_from_snapshot(self, snapshot: RawSnapshot, category_hint: str = None, extractor_type: str = "auto", persist: bool = True, run_ai_enrichment: bool = True, real_prices_only: bool = False) -> List[dict]:
        """Extract records from a snapshot and optionally save them to the database.

        Args:
            snapshot: The raw snapshot to process
            category_hint: Optional category provided by user (e.g. from manual scrape form)
            extractor_type: Optional specific extractor to use
            persist: If False, do not commit records to the database
            run_ai_enrichment: If False, skip the AI enrichment stage to return results immediately
            real_prices_only: If True, only keep records containing an extracted price value.

        Returns:
            List of created record dictionaries
        """
        extractor = self._get_extractor(snapshot, category_hint, extractor_type)
        if not extractor:
            return []

        records = extractor.extract()
        
        # Fallback logic: if no records found with specific extractor, try generic
        if not records and not isinstance(extractor, GenericExtractor):
            logger.info(f"Extractor {extractor.__class__.__name__} found 0 records for snapshot {snapshot.id}. Falling back to GenericExtractor.")
            cat = category_hint or getattr(extractor, 'source_category', None)
            generic_extractor = GenericExtractor(snapshot, cat)
            records = generic_extractor.extract()
        
        # Additional extraction: if a specific extractor found some records, still run generic extraction
        # to capture any extra price/service items missed by the category-specific parser.
        if records and not isinstance(extractor, GenericExtractor):
            cat = category_hint or getattr(extractor, 'source_category', None)
            generic_extractor = GenericExtractor(snapshot, cat)
            extra_records = generic_extractor.extract()
            for extra in extra_records:
                if extra and extra.price_value is not None and extra.confidence_score is not None:
                    if not any(self._is_record_duplicate(extra, existing) for existing in records):
                        records.append(extra)

        if real_prices_only:
            records = [r for r in records if r.price_value is not None]


        created_records = []
        records_to_commit = []
        
        if persist:
            for record in records:
                if not record:
                    continue

                existing = self.db.query(ExtractedRecord).filter(
                    ExtractedRecord.entity_name == record.entity_name,
                    ExtractedRecord.title == record.title,
                    ExtractedRecord.market == record.market,
                    ExtractedRecord.category == record.category
                ).order_by(ExtractedRecord.captured_at.desc()).first()

                is_duplicate = False
                if existing:
                    if (existing.price_value == record.price_value and
                        existing.price_currency == record.price_currency and
                        existing.billing_period == record.billing_period and
                        existing.unit_value == record.unit_value and
                        existing.unit_type == record.unit_type and
                        existing.description == record.description):
                        is_duplicate = True
                        
                if is_duplicate:
                    existing.captured_at = func.now()
                    existing.snapshot_id = snapshot.id
                    self.db.add(existing)
                    records_to_commit.append(existing)
                else:
                    self.db.add(record)
                    records_to_commit.append(record)
            
            try:
                self.db.commit()
                for record in records_to_commit:
                    self.db.refresh(record)
                    created_records.append({
                        "id": record.id,
                        "entity_name": record.entity_name,
                        "category": record.category,
                        "subcategory": record.subcategory,
                        "title": record.title,
                        "price_value": record.price_value,
                        "price_currency": record.price_currency,
                        "captured_at": record.captured_at,
                    })
            except Exception as e:
                self.db.rollback()
                logger.error(f"Failed to commit records for snapshot {snapshot.id}: {e}")
                return []
            # Publish persisted records to configured webhook targets (real-time push)
            try:
                publisher = WebhookPublisher(self.db)
                for rec in records_to_commit:
                    try:
                        publisher.publish_record(rec)
                    except Exception as pub_e:
                        logger.warning(f"Webhook publish failed for record {getattr(rec, 'id', None)}: {pub_e}")
            except Exception as pub_setup_err:
                logger.warning(f"Webhook publishing setup failed: {pub_setup_err}")

            # AI Enrichment Stage (Phase 3 Integration)
            if run_ai_enrichment and settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-api-key-here":
                try:
                    logger.info(f"Triggering AI Intelligence for snapshot {snapshot.id}")
                    intel_service = IntelligenceService(self.db)
                    intel_service.process_snapshot_with_ai(snapshot, extractor)
                except Exception as ai_err:
                    logger.warning(f"AI Enrichment skipped or failed for snapshot {snapshot.id}: {ai_err}")
        else:
            seen = []
            for record in records:
                if not record:
                    continue
                if any(self._is_record_duplicate(record, existing) for existing in seen):
                    continue
                seen.append(record)
                created_records.append({
                    "id": getattr(record, 'id', None),
                    "entity_name": record.entity_name,
                    "category": record.category,
                    "subcategory": record.subcategory,
                    "title": record.title,
                    "price_value": record.price_value,
                    "price_currency": record.price_currency,
                    "captured_at": getattr(record, 'captured_at', None),
                })

        return created_records

    def _is_record_duplicate(self, record_a, record_b) -> bool:
        return (
            record_a.entity_name == record_b.entity_name and
            record_a.title == record_b.title and
            record_a.category == record_b.category and
            record_a.price_value == record_b.price_value and
            record_a.price_currency == record_b.price_currency and
            record_a.billing_period == record_b.billing_period and
            record_a.unit_value == record_b.unit_value and
            record_a.unit_type == record_b.unit_type and
            record_a.description == record_b.description
        )

    def _get_extractor(self, snapshot: RawSnapshot, category_hint: str = None, extractor_type: str = "auto") -> BaseExtractor:
        """Get the appropriate extractor for the snapshot."""
        
        # 1. Honor explicit extractor type if provided (not "auto")
        if extractor_type and extractor_type != "auto":
            ext_type = extractor_type.lower()
            if ext_type == 'telecom':
                return TelecomExtractor(snapshot, 'telecom')
            elif ext_type == 'banking':
                return BankingExtractor(snapshot, 'banking')
            elif ext_type == 'insurance':
                return InsuranceExtractor(snapshot, 'insurance')
            elif ext_type == 'education':
                return EducationExtractor(snapshot, 'education')
            elif ext_type == 'generic':
                return GenericExtractor(snapshot, category_hint or 'service')
            elif ext_type == 'transport':
                return TransportExtractor(snapshot, 'transport')
            elif ext_type == 'hospitality':
                return HospitalityExtractor(snapshot, category_hint or 'hotels')
            elif ext_type == 'econet':
                return EconetExtractor(snapshot, 'telecom')

        # 2. Determine category from hint if provided
        cat = category_hint.lower() if category_hint else None
        
        # 3. Determine category from source if no hint
        if not cat and snapshot.source_page_id:
            source_page = self.db.query(Source).join(Source.pages).filter(
                Source.pages.any(id=snapshot.source_page_id)
            ).first()
            if source_page:
                cat = source_page.category.lower()

        # Return appropriate extractor based on determined category
        if cat:
            if cat == 'telecom':
                return TelecomExtractor(snapshot, cat)
            elif cat == 'banking':
                return BankingExtractor(snapshot, cat)
            elif cat == 'insurance':
                return InsuranceExtractor(snapshot, cat)
            elif cat in ['hotels', 'hospitality']:
                return HospitalityExtractor(snapshot, cat)
            elif cat in ['education', 'universities', 'schools']:
                return EducationExtractor(snapshot, cat)
            elif cat in ['transport', 'mobility']:
                return TransportExtractor(snapshot, cat)
            elif cat in ['utilities', 'solar']:
                return GenericExtractor(snapshot, cat)
            else:
                return GenericExtractor(snapshot, cat)

        # 4. Fallback: determine from URL keywords
        url = snapshot.url.lower()
        if 'econet' in url:
            return EconetExtractor(snapshot, 'telecom')
        elif any(keyword in url for keyword in ['vodafone', 'o2', 'ee', 'three', 'telecom', 'netone', 'safaricom']):
            return TelecomExtractor(snapshot, 'telecom')
        elif any(keyword in url for keyword in ['hsbc', 'barclays', 'bank', 'stanbic', 'cbz', 'fbc', 'nmb']):
            return BankingExtractor(snapshot, 'banking')
        elif any(keyword in url for keyword in ['insurance', 'assurance', 'policy', 'oldmutual', 'zimnat', 'sanlam']):
            return InsuranceExtractor(snapshot, 'insurance')
        elif any(keyword in url for keyword in ['hotel', 'stay', 'booking', 'marriott', 'hilton', 'meikles']):
            return HospitalityExtractor(snapshot, 'hotels')
        elif any(keyword in url for keyword in ['university', 'college', 'school', 'tuition', 'edu', 'fees', 'nust', 'hit']):
            return EducationExtractor(snapshot, 'education')
        elif any(keyword in url for keyword in ['airline', 'fly', 'flight', 'transport', 'shipping', 'dhl', 'fedex', 'zupco']):
            return TransportExtractor(snapshot, 'transport')

        return GenericExtractor(snapshot, 'service')
