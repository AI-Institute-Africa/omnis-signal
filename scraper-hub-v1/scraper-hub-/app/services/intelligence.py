import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import (
    RawSnapshot, Product, Service, PriceEntry, Source
)
from app.scraping.schemas import ExtractionResponse, ProductSchema, ServiceSchema
from app.scraping.extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

class IntelligenceService:
    """Service for high-level product and service intelligence."""

    def __init__(self, db: Session):
        self.db = db

    def process_snapshot_with_ai(self, snapshot: RawSnapshot, extractor: BaseExtractor):
        """Perform AI-driven extraction and intelligence analysis on a snapshot."""
        logger.info(f"Running AI Intelligence Engine for snapshot {snapshot.id}")
        
        # 2. Use Gemini to extract structured products/services
        content = snapshot.content[:20000] 
        extraction: ExtractionResponse = extractor._extract_with_gemini(content)
        
        # 3. Process Products
        for p_schema in extraction.products:
            self._process_product(snapshot, p_schema)
            
        # 4. Process Services
        for s_schema in extraction.services:
            self._process_service(snapshot, s_schema)
            
        self.db.commit()
        return extraction

    def _process_product(self, snapshot: RawSnapshot, schema: ProductSchema):
        # Find existing product
        source_id = self._get_source_id(snapshot)
        
        product = self.db.query(Product).filter(
            Product.source_id == source_id,
            Product.name == schema.name
        ).first()
        
        if not product:
            product = Product(
                source_id=source_id,
                name=schema.name,
                brand=schema.brand,
                category=schema.category,
                sku=schema.sku,
                description=schema.description,
                images=schema.images,
                specifications=schema.specifications,
                tags=schema.tags,
                subcategory=getattr(schema, 'subcategory', None)
            )
            self.db.add(product)
            self.db.flush()
        else:
            product.description = schema.description or product.description
            product.specifications = schema.specifications or product.specifications
            product.images = schema.images or product.images
            
        self._add_price_entry(product=product, price_info=schema.price, snapshot=snapshot)

    def _process_service(self, snapshot: RawSnapshot, schema: ServiceSchema):
        source_id = self._get_source_id(snapshot)
        
        service = self.db.query(Service).filter(
            Service.source_id == source_id,
            Service.name == schema.name
        ).first()
        
        if not service:
            service = Service(
                source_id=source_id,
                name=schema.name,
                category=schema.category,
                description=schema.description,
                features=schema.features,
                requirements=schema.requirements,
                eligibility=schema.eligibility,
                duration=schema.duration,
                subcategory=getattr(schema, 'subcategory', None)
            )
            self.db.add(service)
            self.db.flush()
        else:
            service.description = schema.description or service.description
            service.features = schema.features or service.features
            
        self._add_price_entry(service=service, price_info=schema.price, snapshot=snapshot)

    def _add_price_entry(self, product=None, service=None, price_info=None, snapshot=None):
        # Check latest price to detect change
        latest_price = None
        if product:
            latest_price = self.db.query(PriceEntry).filter(PriceEntry.product_id == product.id).order_by(PriceEntry.captured_at.desc()).first()
        elif service:
            latest_price = self.db.query(PriceEntry).filter(PriceEntry.service_id == service.id).order_by(PriceEntry.captured_at.desc()).first()
            
        is_change = True
        previous_price = None
        if latest_price:
            previous_price = latest_price.price_value
            # If both are None, it's not a change. If values match, it's not a change.
            if latest_price.price_value == price_info.price_value and latest_price.currency == price_info.currency:
                is_change = False
        elif price_info.price_value is None and price_info.currency == 'USD':
            # If no price exists and we are trying to add a None price, maybe skip to avoid bloating
            # But the user wants everything shown, so let's allow the first entry.
            pass
        
        if is_change:
            price_entry = PriceEntry(
                product_id=product.id if product else None,
                service_id=service.id if service else None,
                price_value=price_info.price_value,
                currency=price_info.currency,
                discount_price=price_info.discount_price,
                previous_price=previous_price or price_info.previous_price,
                is_promotion=price_info.is_promotion,
                promotion_details=price_info.promotion_details,
                snapshot_id=snapshot.id,
                source_url=snapshot.url,
                
                # New normalization fields from user table
                normalized_value=price_info.normalized_value,
                normalized_unit=price_info.normalized_unit,
                formula=price_info.formula,
                per_second=price_info.per_second,
                per_minute=price_info.per_minute,
                per_hour=price_info.per_hour,
                daily=price_info.daily,
                three_days=price_info.three_days,
                weekly=price_info.weekly,
                bi_weekly=price_info.bi_weekly,
                monthly=price_info.monthly,
                yearly=price_info.yearly
            )
            self.db.add(price_entry)
            
            logger.info(f"Price change detected for {'product' if product else 'service'}: {price_info.price_value} {price_info.currency}")

    def _get_source_id(self, snapshot: RawSnapshot):
        # Helper to find source_id from snapshot
        source_page = self.db.query(Source).join(Source.pages).filter(
            Source.pages.any(id=snapshot.source_page_id)
        ).first()
        return source_page.id if source_page else None
