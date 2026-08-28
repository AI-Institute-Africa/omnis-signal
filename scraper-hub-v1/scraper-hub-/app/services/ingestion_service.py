"""
Direct Ingestion Service (Mode A) - Automated scraper price landing.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.services.catalog_service import (
    get_sector_by_slug,
    get_category_by_slug,
    get_or_create_provider,
    upsert_listing,
    validate_attributes
)
from app.db.models.catalog import (
    Listing,
    ListingStatus,
    FreshnessStatus,
    ListingUpdateSource
)


class IngestPayload(BaseModel):
    sector_slug: str = Field(..., description="Sector slug, e.g. 'banking'")
    category_slug: str = Field(..., description="Category slug, e.g. 'current_accounts'")
    provider_name: str = Field(..., description="Provider name, e.g. 'CBZ'")
    listing_name: str = Field(..., description="Product/fee name, e.g. 'Gold Savings Account'")
    price: float = Field(..., description="Price value")
    currency: str = Field("USD", description="Currency code")
    source_url: Optional[str] = Field(None, description="The scraped page URL")
    description: Optional[str] = Field(None, description="Product description")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Schema attributes")


class IngestResult(BaseModel):
    listing_id: str
    provider_id: str
    action: str  # 'created' | 'updated' | 'unchanged'
    validation_warnings: List[str] = []

    class Config:
        from_attributes = True


class DirectIngestionService:
    def ingest(self, db: Session, payload: IngestPayload) -> IngestResult:
        """
        Mode A Direct Ingestion Engine:
        1. Resolve sector by slug (must be live)
        2. Resolve category by slug
        3. Validate attributes against schema
        4. Resolve or create provider
        5. Idempotently upsert Listing + previous price snapshot into ListingPriceHistory
        6. Commit and return IngestResult
        """
        # 1. Resolve sector
        sector = get_sector_by_slug(db, payload.sector_slug)
        if not sector:
            raise ValueError(f"Sector '{payload.sector_slug}' not found.")

        # 2. Resolve category
        category = get_category_by_slug(db, sector.id, payload.category_slug)
        if not category:
            raise ValueError(f"Category '{payload.category_slug}' not found under sector '{payload.sector_slug}'.")

        # 3. Validate attributes
        warnings = validate_attributes(db, category.id, payload.attributes)

        # 4. Get or create provider
        provider = get_or_create_provider(
            db,
            name=payload.provider_name,
            source_url=payload.source_url if hasattr(payload, 'source_url') else None
        )

        # 5. Upsert listing
        listing, action = upsert_listing(
            db,
            category_id=category.id,
            provider_id=provider.id,
            name=payload.listing_name,
            price=payload.price,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description,
            status=ListingStatus.PUBLISHED,
            freshness_status=FreshnessStatus.UNVERIFIED,
            last_update_source=ListingUpdateSource.SCRAPER,
        )

        db.commit()

        return IngestResult(
            listing_id=listing.id,
            provider_id=provider.id,
            action=action,
            validation_warnings=warnings
        )


ingestion_service = DirectIngestionService()
