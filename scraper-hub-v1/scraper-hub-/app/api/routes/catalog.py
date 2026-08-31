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
from app.services.banking_service import banking_service
from app.scraping.banking_scraper import run_banking_scraper
from app.services.education_service import education_service
from app.scraping.education_scraper import run_education_scraper
from app.services.food_service import food_service
from app.scraping.food_scraper import run_food_scraper
from app.services.hotels_service import hotels_service
from app.scraping.hotels_scraper import run_hotels_scraper
from app.services.retail_service import retail_service
from app.scraping.retail_scraper import run_retail_scraper
from app.services.telecom_service import telecom_service
from app.scraping.telecom_scraper import run_telecom_scraper
from app.services.transport_service import transport_service
from app.scraping.transport_scraper import run_transport_scraper
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


# ========================================================================
# 6. BANKING SECTOR SPECIALIZED ENDPOINTS
# ========================================================================

class BankingFeeIngestRequest(BaseModel):
    bank_name: str
    revenue_line_slug: str
    listing_name: str
    price: float
    currency: str = "USD"
    attributes: Dict[str, Any] = {}
    source_url: Optional[str] = None
    description: Optional[str] = None


@router.get("/banking/fee-hierarchy", summary="Get 3-level banking fee hierarchy")
def get_banking_fee_hierarchy(db: Session = Depends(get_db)):
    """Returns the full 3-level fee tree (fee_category -> subcategory -> revenue_line)."""
    return banking_service.get_fee_hierarchy(db)


@router.get("/banking/flat-categories", summary="Get flat consumer banking categories")
def get_banking_flat_categories(db: Session = Depends(get_db)):
    """Returns the 4 flat consumer categories (savings, current, nostro FCA, banks)."""
    return banking_service.get_flat_categories(db)


@router.get("/banking/banks", summary="Get Zimbabwean banks directory and channels")
def get_banking_banks_directory(db: Session = Depends(get_db)):
    """Returns all 23 banks with USSD codes, channel capabilities, and directory listing."""
    return banking_service.get_banks_directory(db)


@router.post("/banking/ingest-fee", summary="Ingest fee into revenue line")
def ingest_banking_fee(payload: BankingFeeIngestRequest, db: Session = Depends(get_db)):
    """Automated fee ingestion into a specific revenue line."""
    try:
        return banking_service.ingest_fee(
            db,
            bank_name=payload.bank_name,
            revenue_line_slug=payload.revenue_line_slug,
            listing_name=payload.listing_name,
            price=payload.price,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fee ingestion failed: {str(e)}")


@router.post("/banking/run-scraper", summary="Trigger automated banking scraper")
def trigger_banking_scraper(db: Session = Depends(get_db)):
    """Executes the automated Zimbabwean banking charges and fee scraper."""
    return run_banking_scraper(db)


# ========================================================================
# 7. EDUCATION SECTOR SPECIALIZED ENDPOINTS
# ========================================================================

class EducationListingIngestRequest(BaseModel):
    institution_name: str
    category_slug: str
    listing_name: str
    price: float
    currency: str = "USD"
    attributes: Dict[str, Any] = {}
    source_url: Optional[str] = None
    description: Optional[str] = None


@router.get("/education/categories", summary="Get education categories and schemas")
def get_education_categories(db: Session = Depends(get_db)):
    """Returns the 3 education categories (primary, secondary, university) with schemas."""
    return education_service.get_categories(db)


@router.get("/education/institutions", summary="Get education institutions and listings")
def get_education_institutions(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    db: Session = Depends(get_db)
):
    """Returns educational institutions and their fee listings."""
    return education_service.get_institutions(db, category_slug=category)


@router.post("/education/ingest", summary="Ingest education fee listing")
def ingest_education_listing(payload: EducationListingIngestRequest, db: Session = Depends(get_db)):
    """Automated ingestion of education fee listing with normalisation."""
    try:
        return education_service.ingest_listing(
            db,
            institution_name=payload.institution_name,
            category_slug=payload.category_slug,
            listing_name=payload.listing_name,
            price=payload.price,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Education ingestion failed: {str(e)}")


@router.post("/education/run-scraper", summary="Trigger automated education scraper")
def trigger_education_scraper(db: Session = Depends(get_db)):
    """Executes the automated education fees and tuition scraper."""
    return run_education_scraper(db)


# ========================================================================
# 8. FOOD & DRINK SECTOR SPECIALIZED ENDPOINTS
# ========================================================================

class FoodMenuIngestRequest(BaseModel):
    restaurant_name: str
    category_slug: str
    menu_item_name: str
    price: float
    currency: str = "USD"
    attributes: Dict[str, Any] = {}
    source_url: Optional[str] = None
    description: Optional[str] = None


@router.get("/food/categories", summary="Get Food & Drink categories and schemas")
def get_food_categories(db: Session = Depends(get_db)):
    """Returns the 2 food categories (fast-food, casual-dining) with schemas."""
    return food_service.get_categories(db)


@router.get("/food/restaurants", summary="Get restaurants and menu listings")
@router.get("/food/items", summary="Get restaurants and menu listings (alias)")
def get_food_restaurants(
    category: Optional[str] = Query(None, description="Filter by category slug (fast-food, casual-dining)"),
    db: Session = Depends(get_db)
):
    """Returns restaurant chains and their active menu listings."""
    return food_service.get_restaurants(db, category_slug=category)


@router.post("/food/ingest", summary="Ingest a menu item listing")
def ingest_food_menu_item(payload: FoodMenuIngestRequest, db: Session = Depends(get_db)):
    """Automated ingestion of a single restaurant menu item into the catalog."""
    try:
        return food_service.ingest_menu_item(
            db,
            restaurant_name=payload.restaurant_name,
            category_slug=payload.category_slug,
            menu_item_name=payload.menu_item_name,
            price=payload.price,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Food ingestion failed: {str(e)}")


@router.post("/food/run-scraper", summary="Trigger automated Food & Drink scraper")
def trigger_food_scraper(db: Session = Depends(get_db)):
    """Executes the automated Food & Drink restaurant menu scraper."""
    return run_food_scraper(db)


# ========================================================================
# 9. HOTELS SECTOR SPECIALIZED ENDPOINTS
# ========================================================================

class HotelRoomIngestRequest(BaseModel):
    hotel_name: str
    room_name: str
    price_per_night: float
    currency: str = "USD"
    attributes: Dict[str, Any] = {}
    source_url: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = []


@router.get("/hotels/category", summary="Get Hotels category and schema")
def get_hotels_category(db: Session = Depends(get_db)):
    """Returns the hotel-stays category with its 5 attribute schema fields."""
    try:
        return hotels_service.get_category(db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/hotels/listings", summary="Get hotel room rate listings")
@router.get("/hotels/stays", summary="Get hotel room rate listings (alias)")
def get_hotels_listings(db: Session = Depends(get_db)):
    """Returns all hotel room listings with night rates and amenities."""
    return hotels_service.get_listings(db)


@router.post("/hotels/ingest", summary="Ingest a hotel room listing")
def ingest_hotel_room(payload: HotelRoomIngestRequest, db: Session = Depends(get_db)):
    """Automated ingestion of a hotel room rate into the catalog."""
    try:
        return hotels_service.ingest_room_listing(
            db,
            hotel_name=payload.hotel_name,
            room_name=payload.room_name,
            price_per_night=payload.price_per_night,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description,
            images=payload.images
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotels ingestion failed: {str(e)}")


@router.post("/hotels/run-scraper", summary="Trigger automated Hotels scraper")
def trigger_hotels_scraper(db: Session = Depends(get_db)):
    """Executes the automated Zimbabwean hotel room rate scraper."""
    return run_hotels_scraper(db)


# ========================================================================
# 10. RETAIL & GROCERIES SECTOR SPECIALIZED ENDPOINTS
# ========================================================================

class RetailProductIngestRequest(BaseModel):
    supplier_name: str
    category_slug: str
    product_name: str
    price: float
    currency: str = "USD"
    attributes: Dict[str, Any] = {}
    source_url: Optional[str] = None
    description: Optional[str] = None


@router.get("/retail/categories", summary="Get all 25 Retail categories and schemas")
def get_retail_categories(db: Session = Depends(get_db)):
    """Returns all 25 retail categories with the common 12-field attribute schema."""
    return retail_service.get_categories(db)


@router.get("/retail/products", summary="Get retail product listings")
def get_retail_products(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    db: Session = Depends(get_db)
):
    """Returns retail commodity products with unit prices and supplier info."""
    return retail_service.get_products(db, category_slug=category, brand=brand)


@router.post("/retail/ingest", summary="Ingest a retail product listing")
def ingest_retail_product(payload: RetailProductIngestRequest, db: Session = Depends(get_db)):
    """Automated ingestion of a retail commodity with unit-price calculation."""
    try:
        return retail_service.ingest_product_listing(
            db,
            supplier_name=payload.supplier_name,
            category_slug=payload.category_slug,
            product_name=payload.product_name,
            price=payload.price,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retail ingestion failed: {str(e)}")


@router.post("/retail/run-scraper", summary="Trigger automated Retail scraper")
def trigger_retail_scraper(db: Session = Depends(get_db)):
    """Executes the automated Retail & Groceries commodity scraper."""
    return run_retail_scraper(db)


# ========================================================================
# 11. TELECOM SECTOR SPECIALIZED ENDPOINTS
# ========================================================================

class TelecomBundleIngestRequest(BaseModel):
    operator_name: str
    category_slug: str
    bundle_name: str
    price: float
    currency: str = "USD"
    attributes: Dict[str, Any] = {}
    source_url: Optional[str] = None
    description: Optional[str] = None


@router.get("/telecom/categories", summary="Get all 8 Telecom bundle categories and schemas")
def get_telecom_categories(db: Session = Depends(get_db)):
    """Returns all 8 telecom categories with the 6-field attribute schema."""
    return telecom_service.get_categories(db)


@router.get("/telecom/bundles", summary="Get mobile data and bundle listings")
def get_telecom_bundles(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    operator: Optional[str] = Query(None, description="Filter by operator (Econet, NetOne, Telecel)"),
    db: Session = Depends(get_db)
):
    """Returns telecom bundle offers with validity, data allowance, and price per GB."""
    return telecom_service.get_bundles(db, category_slug=category, operator=operator)


@router.post("/telecom/ingest", summary="Ingest a telecom bundle listing")
def ingest_telecom_bundle(payload: TelecomBundleIngestRequest, db: Session = Depends(get_db)):
    """Automated ingestion of a telecom bundle with operator normalisation and price_per_gb calculation."""
    try:
        return telecom_service.ingest_bundle_listing(
            db,
            operator_name=payload.operator_name,
            category_slug=payload.category_slug,
            bundle_name=payload.bundle_name,
            price=payload.price,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telecom ingestion failed: {str(e)}")


@router.post("/telecom/run-scraper", summary="Trigger automated Telecom scraper")
def trigger_telecom_scraper(db: Session = Depends(get_db)):
    """Executes the automated Telecom mobile data and bundle scraper."""
    return run_telecom_scraper(db)


# ========================================================================
# 12. TRANSPORT SECTOR SPECIALIZED ENDPOINTS
# ========================================================================

class TransportServiceIngestRequest(BaseModel):
    operator_name: str
    category_slug: str
    service_name: str
    fare_gazetted: Optional[float] = None
    fare_estimate: Optional[float] = None
    price: Optional[float] = None
    currency: str = "USD"
    attributes: Dict[str, Any] = {}
    source_url: Optional[str] = None
    description: Optional[str] = None


@router.get("/transport/categories", summary="Get all 8 Transport categories and schemas")
def get_transport_categories(db: Session = Depends(get_db)):
    """Returns all 8 transport categories with the common 16-field attribute schema."""
    return transport_service.get_categories(db)


@router.get("/transport/services", summary="Get transport services and fares")
def get_transport_services(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    province: Optional[str] = Query(None, description="Filter by province/district/route"),
    ownership: Optional[str] = Query(None, description="Filter by ownership (state, private, cooperative, franchise)"),
    db: Session = Depends(get_db)
):
    """Returns transport operator services with gazetted fares and route coverage."""
    return transport_service.get_services(db, category_slug=category, province_district=province, ownership_status=ownership)


@router.post("/transport/ingest", summary="Ingest a transport route/service listing")
def ingest_transport_service(payload: TransportServiceIngestRequest, db: Session = Depends(get_db)):
    """Automated ingestion of a transport operator service with fare mapping."""
    try:
        return transport_service.ingest_transport_listing(
            db,
            operator_name=payload.operator_name,
            category_slug=payload.category_slug,
            service_name=payload.service_name,
            fare_gazetted=payload.fare_gazetted,
            fare_estimate=payload.fare_estimate,
            price=payload.price,
            currency=payload.currency,
            attributes=payload.attributes,
            source_url=payload.source_url,
            description=payload.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transport ingestion failed: {str(e)}")


@router.post("/transport/run-scraper", summary="Trigger automated Transport scraper")
def trigger_transport_scraper(db: Session = Depends(get_db)):
    """Executes the automated Transport transit fare scraper."""
    return run_transport_scraper(db)




