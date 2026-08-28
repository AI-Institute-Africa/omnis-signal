"""
Catalog API Routes - Endpoints for Sectors, Categories, Attribute Schemas,
Providers, Listings, Price History, and Mode B Scrape Review Queue.
"""
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.ingestion_service import (
    DirectIngestionService,
    IngestPayload,
    IngestResult,
    ingestion_service
)
from app.services.catalog_service import (
    get_sector_by_slug,
    get_category_by_slug,
    get_or_create_provider,
    upsert_listing
)
from app.db.models.catalog import (
    SectorConfig,
    Category,
    AttributeSchemaField,
    Provider,
    Listing,
    ListingPriceHistory,
    ScrapeSource,
    ScrapedItem,
    SectorStatus,
    ListingStatus,
    ScrapeItemStatus,
    ScrapeTrigger
)


def _uid() -> str:
    return str(uuid.uuid4())


router = APIRouter(prefix="/catalog", tags=["catalog"])


# ------------------------------------------------------------------------
# Pydantic Request Schemas for Mode B Queue
# ------------------------------------------------------------------------

class ScrapeItemSubmitRequest(BaseModel):
    source_url: Optional[str] = None
    category_id: Optional[str] = None
    raw_content: Optional[str] = None
    extracted_data: Dict[str, Any]
    confidence: Optional[float] = None
    suggested_provider_id: Optional[str] = None
    suggested_listing_id: Optional[str] = None
    triggered_by: str = ScrapeTrigger.ADMIN_MANUAL


class RejectionRequest(BaseModel):
    reason: str = Field(..., description="Reason for rejecting this item")


# ========================================================================
# 1. SECTORS & CATEGORIES
# ========================================================================

@router.get("/sectors", summary="List all live sectors")
def list_sectors(db: Session = Depends(get_db)):
    """Returns all sectors with status=live."""
    sectors = db.query(SectorConfig).filter(
        SectorConfig.status == SectorStatus.LIVE
    ).all()
    return [s.to_dict() for s in sectors]


@router.get("/sectors/{slug}/categories", summary="Get categories for a sector")
def get_sector_categories(slug: str, db: Session = Depends(get_db)):
    """Returns all categories under a given sector slug."""
    sector = get_sector_by_slug(db, slug)
    if not sector:
        raise HTTPException(status_code=404, detail=f"Sector '{slug}' not found.")

    cats = db.query(Category).filter(
        Category.sector_id == sector.id
    ).all()
    return [c.to_dict() for c in cats]


@router.get("/categories/{category_id}/schema", summary="Get attribute schema for a category")
def get_category_schema(category_id: str, db: Session = Depends(get_db)):
    """Returns the attribute schema fields contract for a category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    fields = db.query(AttributeSchemaField).filter(
        AttributeSchemaField.category_id == category_id
    ).order_by(AttributeSchemaField.sort_order).all()

    return {
        "category_id": category.id,
        "category_slug": category.slug,
        "category_name": category.name,
        "schema_fields": [f.to_dict() for f in fields]
    }


# ========================================================================
# 2. PROVIDERS
# ========================================================================

@router.get("/providers", summary="List all providers")
def list_providers(
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Returns providers listed in the catalog."""
    providers = db.query(Provider).order_by(Provider.name).offset(offset).limit(limit).all()
    return [p.to_dict() for p in providers]


# ========================================================================
# 3. MODE A: DIRECT WRITE INGEST LISTING
# ========================================================================

@router.post("/ingest", response_model=IngestResult, summary="Mode A Direct Ingestion")
def ingest_listing(payload: IngestPayload, db: Session = Depends(get_db)):
    """
    Mode A Direct Ingestion Endpoint:
    Automated scrapers land product data directly into Provider + Listing + ListingPriceHistory.
    """
    try:
        result = ingestion_service.ingest(db, payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


# ========================================================================
# 4. LISTINGS & PRICE HISTORY
# ========================================================================

@router.get("/listings", summary="Query listings")
def list_listings(
    sector: Optional[str] = Query(None, description="Sector slug"),
    category: Optional[str] = Query(None, description="Category slug"),
    provider: Optional[str] = Query(None, description="Provider name or ID"),
    status: Optional[str] = Query(ListingStatus.PUBLISHED, description="Listing status"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Query scraped product listings with filters on sector, category, provider, and status."""
    q = db.query(Listing)

    if status:
        q = q.filter(Listing.status == status)

    if sector:
        q = q.join(Category, Listing.category_id == Category.id)
        q = q.join(SectorConfig, Category.sector_id == SectorConfig.id)
        q = q.filter(SectorConfig.slug == sector)

    if category:
        if not sector:
            q = q.join(Category, Listing.category_id == Category.id)
        q = q.filter(Category.slug == category)

    if provider:
        q = q.join(Provider, Listing.provider_id == Provider.id)
        q = q.filter(
            (Provider.id == provider) | (Provider.name == provider)
        )

    results = q.order_by(Listing.last_verified_at.desc()).offset(offset).limit(limit).all()
    return [l.to_dict() for l in results]


@router.get("/listings/{listing_id}", summary="Get a single listing")
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    """Returns details for a specific listing_id."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    return listing.to_dict()


@router.get("/listings/{listing_id}/price-history", summary="Get price trend history")
def get_price_history(listing_id: str, db: Session = Depends(get_db)):
    """Returns previous price snapshots for sparkline and price-drop features."""
    hist = db.query(ListingPriceHistory).filter(
        ListingPriceHistory.listing_id == listing_id
    ).order_by(ListingPriceHistory.recorded_at.asc()).all()
    return [h.to_dict() for h in hist]


# ========================================================================
# 5. MODE B: HUMAN-REVIEW QUEUE (ScrapedItems)
# ========================================================================

@router.post("/scrape-queue", summary="Submit a scraped item for review")
def submit_scrape_item(request: ScrapeItemSubmitRequest, db: Session = Depends(get_db)):
    """Submits a scraped candidate for human vetting (Mode B)."""
    item = ScrapedItem(
        id=_uid(),
        category_id=request.category_id,
        source_url=request.source_url,
        triggered_by=request.triggered_by,
        raw_content=request.raw_content,
        confidence=request.confidence,
        suggested_provider_id=request.suggested_provider_id,
        suggested_listing_id=request.suggested_listing_id,
        status=ScrapeItemStatus.PENDING,
    )
    item.extracted_data = request.extracted_data
    db.add(item)
    db.commit()
    return item.to_dict()


@router.get("/scrape-queue", summary="List pending scraped items")
def list_scrape_queue(
    status: str = Query(ScrapeItemStatus.PENDING),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Returns candidates awaiting admin review."""
    items = db.query(ScrapedItem).filter(
        ScrapedItem.status == status
    ).order_by(ScrapedItem.created_at.desc()).offset(offset).limit(limit).all()
    return [i.to_dict() for i in items]


@router.patch("/scrape-queue/{item_id}/approve", summary="Approve a candidate into a listing")
def approve_scraped_item(item_id: str, db: Session = Depends(get_db)):
    """
    Approves a pending ScrapedItem, transferring its extracted_data directly into the Listing table.
    """
    item = db.query(ScrapedItem).filter(ScrapedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="ScrapedItem not found.")

    data = item.extracted_data or {}
    provider_name = data.get('providerNameGuess', 'Unknown Provider')
    category_id = item.category_id

    if not category_id:
        raise HTTPException(status_code=400, detail="Candidate has no category_id.")

    provider = get_or_create_provider(db, name=provider_name)
    listing, _ = upsert_listing(
        db,
        category_id=category_id,
        provider_id=provider.id,
        name=data.get('name', 'Unnamed Product'),
        price=float(data.get('price', 0.0)),
        currency=data.get('currency', 'USD'),
        attributes=data.get('attributes', {}),
        source_url=item.source_url,
        description=data.get('description'),
        status=ListingStatus.PUBLISHED,
    )

    item.status = ScrapeItemStatus.APPROVED
    item.suggested_listing_id = listing.id
    db.commit()

    return {
        "status": "approved",
        "listing": listing.to_dict()
    }


@router.patch("/scrape-queue/{item_id}/reject", summary="Reject a candidate")
def reject_scraped_item(item_id: str, request: RejectionRequest, db: Session = Depends(get_db)):
    """Rejects a pending ScrapedItem with a reason."""
    item = db.query(ScrapedItem).filter(ScrapedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="ScrapedItem not found.")

    item.status = ScrapeItemStatus.REJECTED
    item.rejection_reason = request.reason
    db.commit()

    return {
        "status": "rejected",
        "item_id": item.id,
        "rejection_reason": item.rejection_reason
    }
