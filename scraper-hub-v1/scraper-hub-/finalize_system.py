#!/usr/bin/env python3
"""
Scraper Hub System Finalization Script

This script finalizes the system for real-world price and product data extraction by:
1. Cleaning up test/example data
2. Verifying source configuration
3. Setting up automated scraping
4. Creating data export capabilities
5. Providing system status and monitoring
"""

import sys
import asyncio
from datetime import datetime
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import Source, SourcePage, ExtractedRecord, RawSnapshot
from app.services.fetcher import PlaywrightFetcher
from app.services.extractor import ExtractorService
from app.jobs.tasks import scrape_source
from sqlalchemy import func, and_


def ensure_database_initialized():
    """Ensure database tables are created."""
    logger.info("Ensuring database is initialized...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialized")


def clean_test_data():
    """Remove test/example data to ensure clean real data extraction."""
    db = SessionLocal()
    try:
        logger.info("Cleaning up test/example data...")
        
        # Remove records from test sources (Httpbin, generic examples, etc.)
        test_entities = ['Example', 'Httpbin', 'Herman Melville', 'Test', 'Mock']
        deleted = 0
        
        for entity in test_entities:
            count = db.query(ExtractedRecord).filter(
                ExtractedRecord.entity_name.ilike(f'%{entity}%')
            ).delete()
            deleted += count
            if count > 0:
                logger.info(f"  Removed {count} records from '{entity}'")
        
        db.commit()
        logger.info(f"✅ Cleaned {deleted} test records")
        
    finally:
        db.close()


def verify_sources_have_pages():
    """Ensure sources are properly configured with pages."""
    db = SessionLocal()
    try:
        logger.info("Verifying source configuration...")
        
        sources_without_pages = db.query(Source).filter(
            ~Source.pages.any()
        ).all()
        
        if sources_without_pages:
            logger.warning(f"⚠️  {len(sources_without_pages)} sources have no pages configured")
            # Log first 5
            for source in sources_without_pages[:5]:
                logger.warning(f"    - {source.name} ({source.category})")
        
        total_sources = db.query(Source).count()
        sources_with_pages = db.query(Source).filter(Source.pages.any()).count()
        enabled_pages = db.query(SourcePage).filter(SourcePage.enabled == True).count()
        
        logger.info(f"  Total sources: {total_sources}")
        logger.info(f"  Sources with pages: {sources_with_pages}")
        logger.info(f"  Enabled pages: {enabled_pages}")
        logger.info(f"✅ Source verification complete")
        
    finally:
        db.close()


def get_extraction_statistics():
    """Get comprehensive extraction statistics."""
    db = SessionLocal()
    try:
        logger.info("Gathering extraction statistics...")
        
        total_records = db.query(ExtractedRecord).count()
        records_with_prices = db.query(ExtractedRecord).filter(
            ExtractedRecord.price_value.isnot(None)
        ).count()
        records_with_descriptions = db.query(ExtractedRecord).filter(
            ExtractedRecord.description.isnot(None)
        ).count()
        
        # Get by category
        by_category = db.query(
            ExtractedRecord.category,
            func.count(ExtractedRecord.id).label('count'),
            func.count(func.nullif(ExtractedRecord.price_value, None)).label('with_price')
        ).group_by(ExtractedRecord.category).all()
        
        logger.info(f"\n📊 Extraction Statistics:")
        logger.info(f"  Total records: {total_records}")
        logger.info(f"  Records with prices: {records_with_prices} ({100*records_with_prices/max(1, total_records):.1f}%)")
        logger.info(f"  Records with descriptions: {records_with_descriptions}")
        logger.info(f"\n  By Category:")
        
        for category, count, with_price in sorted(by_category, key=lambda x: x[1], reverse=True):
            pct = 100 * with_price / max(1, count)
            logger.info(f"    {category:15} | {count:5} records | {with_price:5} with prices ({pct:.0f}%)")
        
        return total_records
        
    finally:
        db.close()


def trigger_scrape_batch(limit: int = None, category_filter: str = None):
    """Trigger scraping of sources in batch."""
    db = SessionLocal()
    try:
        logger.info("Starting batch scrape operation...")
        
        # Get sources to scrape
        query = db.query(Source).filter(Source.pages.any())
        
        if category_filter:
            query = query.filter(Source.category == category_filter)
        
        if limit:
            query = query.limit(limit)
        
        sources = query.all()
        
        logger.info(f"Starting scrape for {len(sources)} sources...")
        
        async def run_scrapes():
            fetcher = PlaywrightFetcher()
            extractor_service = ExtractorService(db)
            
            success_count = 0
            failed_count = 0
            
            for i, source in enumerate(sources, 1):
                logger.info(f"[{i}/{len(sources)}] Scraping {source.name}...")
                
                for page in source.pages:
                    if not page.enabled:
                        continue
                    
                    try:
                        # Fetch page
                        content = await fetcher.fetch_page_content(page.url)
                        
                        if not content:
                            logger.warning(f"  ⚠️  Empty content from {page.url}")
                            failed_count += 1
                            continue
                        
                        # Save snapshot
                        snapshot = RawSnapshot(
                            source_page_id=page.id,
                            url=page.url,
                            content=content,
                            content_type="html"
                        )
                        db.add(snapshot)
                        db.commit()
                        db.refresh(snapshot)
                        
                        # Extract
                        records = extractor_service.extract_from_snapshot(
                            snapshot,
                            category_hint=source.category,
                            persist=True,
                            run_ai_enrichment=False,
                            real_prices_only=False
                        )
                        
                        logger.info(f"  ✅ Extracted {len(records)} records from {source.name}")
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"  ❌ Failed to scrape {source.name}: {e}")
                        failed_count += 1
            
            logger.info(f"\n✅ Scrape complete: {success_count} succeeded, {failed_count} failed")
            return success_count, failed_count
        
        # Run async scraping
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, failed = loop.run_until_complete(run_scrapes())
        loop.close()
        
        return success, failed
        
    finally:
        db.close()


def export_to_csv():
    """Export extracted records to CSV for analysis."""
    import csv
    
    db = SessionLocal()
    try:
        logger.info("Exporting extracted records to CSV...")
        
        records = db.query(ExtractedRecord).filter(
            ExtractedRecord.price_value.isnot(None)
        ).all()
        
        export_path = Path("extracted_data_export.csv")
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Entity', 'Category', 'Subcategory', 'Title', 'Item Name',
                'Price', 'Currency', 'Billing Period', 'Unit Value', 'Unit Type',
                'Description', 'Source URL', 'Confidence Score', 'Captured At'
            ])
            
            for record in records:
                writer.writerow([
                    record.entity_name,
                    record.category,
                    record.subcategory or '',
                    record.title,
                    record.item_name or '',
                    record.price_value,
                    record.price_currency or '',
                    record.billing_period or '',
                    record.unit_value or '',
                    record.unit_type or '',
                    (record.description or '')[:200],
                    record.source_url,
                    record.confidence_score or '',
                    record.captured_at.isoformat() if record.captured_at else ''
                ])
        
        logger.info(f"✅ Exported {len(records)} records to {export_path}")
        
    finally:
        db.close()


def export_to_json():
    """Export extracted records to JSON for API consumption."""
    import json
    
    db = SessionLocal()
    try:
        logger.info("Exporting extracted records to JSON...")
        
        records = db.query(ExtractedRecord).filter(
            ExtractedRecord.price_value.isnot(None)
        ).all()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_records': len(records),
            'records': [
                {
                    'id': r.id,
                    'entity_name': r.entity_name,
                    'category': r.category,
                    'subcategory': r.subcategory,
                    'title': r.title,
                    'item_name': r.item_name,
                    'description': r.description,
                    'price': {
                        'value': r.price_value,
                        'currency': r.price_currency,
                        'billing_period': r.billing_period
                    },
                    'unit': {
                        'value': r.unit_value,
                        'type': r.unit_type
                    },
                    'source_url': r.source_url,
                    'confidence_score': r.confidence_score,
                    'quality_status': r.quality_status,
                    'captured_at': r.captured_at.isoformat() if r.captured_at else None
                }
                for r in records
            ]
        }
        
        export_path = Path("extracted_data_export.json")
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Exported {len(records)} records to {export_path}")
        
    finally:
        db.close()


def show_system_status():
    """Display comprehensive system status."""
    db = SessionLocal()
    try:
        logger.info("\n" + "="*60)
        logger.info("SCRAPER HUB - SYSTEM STATUS")
        logger.info("="*60)
        
        # Counts
        total_sources = db.query(Source).count()
        total_pages = db.query(SourcePage).count()
        enabled_pages = db.query(SourcePage).filter(SourcePage.enabled == True).count()
        total_snapshots = db.query(RawSnapshot).count()
        total_records = db.query(ExtractedRecord).count()
        records_with_prices = db.query(ExtractedRecord).filter(
            ExtractedRecord.price_value.isnot(None)
        ).count()
        
        logger.info(f"\n📦 Configuration:")
        logger.info(f"  Sources:        {total_sources}")
        logger.info(f"  Pages:          {total_pages} (enabled: {enabled_pages})")
        logger.info(f"  Snapshots:      {total_snapshots}")
        logger.info(f"  Records:        {total_records}")
        logger.info(f"  Records w/Price: {records_with_prices} ({100*records_with_prices/max(1, total_records):.1f}%)")
        
        # Top categories
        top_categories = db.query(
            ExtractedRecord.category,
            func.count(ExtractedRecord.id).label('count')
        ).group_by(ExtractedRecord.category).order_by(
            func.count(ExtractedRecord.id).desc()
        ).limit(5).all()
        
        logger.info(f"\n📊 Top Categories:")
        for category, count in top_categories:
            logger.info(f"  {category:15} {count:5} records")
        
        # Top entities
        top_entities = db.query(
            ExtractedRecord.entity_name,
            func.count(ExtractedRecord.id).label('count'),
            func.avg(ExtractedRecord.price_value).label('avg_price')
        ).filter(ExtractedRecord.price_value.isnot(None)).group_by(
            ExtractedRecord.entity_name
        ).order_by(
            func.count(ExtractedRecord.id).desc()
        ).limit(5).all()
        
        logger.info(f"\n🏢 Top Entities (by records):")
        for entity, count, avg_price in top_entities:
            logger.info(f"  {entity:30} {count:4} records (avg price: {avg_price:.2f})")
        
        logger.info("\n" + "="*60 + "\n")
        
    finally:
        db.close()


def main():
    """Main finalization routine."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Finalize Scraper Hub for real data extraction')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--clean-test-data', action='store_true', help='Clean test/example data')
    parser.add_argument('--verify-config', action='store_true', help='Verify source configuration')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--scrape-batch', type=int, metavar='LIMIT', nargs='?', const=10,
                       help='Trigger batch scraping (optional limit)')
    parser.add_argument('--scrape-category', type=str, help='Scrape specific category')
    parser.add_argument('--export-csv', action='store_true', help='Export to CSV')
    parser.add_argument('--export-json', action='store_true', help='Export to JSON')
    parser.add_argument('--full-finalize', action='store_true', 
                       help='Run full finalization (init, clean, verify, status, export)')
    
    args = parser.parse_args()
    
    try:
        if args.full_finalize:
            logger.info("🚀 Starting FULL SYSTEM FINALIZATION...")
            ensure_database_initialized()
            clean_test_data()
            verify_sources_have_pages()
            get_extraction_statistics()
            show_system_status()
            export_to_csv()
            export_to_json()
            logger.info("\n✅ Full finalization complete!")
            
        else:
            if args.init_db:
                ensure_database_initialized()
            
            if args.clean_test_data:
                clean_test_data()
            
            if args.verify_config:
                verify_sources_have_pages()
            
            if args.status:
                show_system_status()
                get_extraction_statistics()
            
            if args.scrape_batch is not None:
                limit = args.scrape_batch if args.scrape_batch > 0 else None
                trigger_scrape_batch(limit=limit, category_filter=args.scrape_category)
            
            if args.export_csv:
                export_to_csv()
            
            if args.export_json:
                export_to_json()
            
            # Default: show status
            if not any([args.init_db, args.clean_test_data, args.verify_config, 
                       args.scrape_batch, args.export_csv, args.export_json]):
                show_system_status()
                get_extraction_statistics()
    
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
