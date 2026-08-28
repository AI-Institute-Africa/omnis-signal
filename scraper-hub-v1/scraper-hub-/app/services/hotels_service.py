"""
Hotels Service — Manages hotel providers, room categories, attribute schemas,
room_type enum normalisation, and automated nightly rate ingestion.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.models.catalog import (
    SectorConfig, Category, AttributeSchemaField, Provider,
    Listing, ListingPriceHistory,
    SectorStatus, CategoryLevel, ListingStatus, FreshnessStatus, ListingUpdateSource
)
from app.services.catalog_service import (
    get_or_create_provider,
    upsert_listing,
    validate_attributes
)


CANONICAL_ROOM_TYPES = {
    "standard": "standard",
    "std": "standard",
    "classic": "standard",
    "deluxe": "deluxe",
    "dlx": "deluxe",
    "luxury": "deluxe",
    "superior": "deluxe",
    "executive": "executive",
    "club": "executive",
    "business": "executive",
    "suite": "suite",
    "presidential": "suite",
    "junior suite": "suite",
    "family": "family",
    "family room": "family",
    "studio": "studio",
    "villa": "villa",
    "chalet": "villa",
    "lodge": "villa",
    "double": "double",
    "twin": "twin",
    "king": "king",
    "queen": "double"
}


class HotelsService:
    @staticmethod
    def get_hotels_sector(db: Session) -> SectorConfig:
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "hotels").first()
        if not sector:
            raise ValueError("Hotels sector not found in database.")
        return sector

    @staticmethod
    def get_category(db: Session) -> Dict[str, Any]:
        """Returns the single hotel-stays category with its attribute schema."""
        sector = HotelsService.get_hotels_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == "hotel-stays"
        ).first()

        if not cat:
            raise ValueError("Category 'hotel-stays' not found under Hotels sector.")

        c_dict = cat.to_dict()
        fields = db.query(AttributeSchemaField).filter(
            AttributeSchemaField.category_id == cat.id
        ).order_by(AttributeSchemaField.sort_order).all()
        c_dict["schema_fields"] = [f.to_dict() for f in fields]
        return c_dict

    @staticmethod
    def get_listings(db: Session) -> List[Dict[str, Any]]:
        """Returns all hotel room rate listings."""
        sector = HotelsService.get_hotels_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == "hotel-stays"
        ).first()

        if not cat:
            return []

        listings = db.query(Listing).filter(Listing.category_id == cat.id).all()
        results = []
        for l in listings:
            p = l.provider
            results.append({
                "listing_id": l.id,
                "hotel_id": p.id if p else l.provider_id,
                "hotel_name": p.name if p else l.name,
                "room_name": l.name,
                "price_per_night": l.price,
                "currency": l.currency,
                "attributes": l.attributes or {},
                "source_url": l.source_url or (p.website_url if p else None),
                "corporate_domain": p.corporate_domain if p else None,
                "rating": l.rating,
                "review_count": l.review_count,
                "last_verified_at": l.last_verified_at.isoformat() if l.last_verified_at else None
            })

        return results

    @staticmethod
    def normalise_room_type(val: Optional[str]) -> str:
        if not val:
            return "standard"
        cleaned = str(val).strip().lower()
        return CANONICAL_ROOM_TYPES.get(cleaned, "standard")

    @staticmethod
    def ingest_room_listing(
        db: Session,
        hotel_name: str,
        room_name: str,
        price_per_night: float,
        currency: str = "USD",
        attributes: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None,
        images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Direct DB write ingestion for a hotel room listing.
        Handles room_type normalisation and sets price = price_per_night.
        """
        sector = HotelsService.get_hotels_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == "hotel-stays"
        ).first()

        if not cat:
            raise ValueError("Category 'hotel-stays' not found under Hotels sector.")

        attrs = attributes.copy() if attributes else {}

        # Normalise room_type
        if "room_type" in attrs:
            attrs["room_type"] = HotelsService.normalise_room_type(attrs["room_type"])
        else:
            attrs["room_type"] = "standard"

        # Sync price_per_night in attributes
        attrs["price_per_night"] = float(price_per_night)

        provider = get_or_create_provider(db, name=hotel_name, source_url=source_url)
        warnings = validate_attributes(db, cat.id, attrs)

        listing, action = upsert_listing(
            db,
            category_id=cat.id,
            provider_id=provider.id,
            name=room_name,
            price=float(price_per_night),
            currency=currency,
            attributes=attrs,
            source_url=source_url,
            description=description,
            images=images or [],
            status=ListingStatus.PUBLISHED,
            freshness_status=FreshnessStatus.UNVERIFIED,
            last_update_source=ListingUpdateSource.SCRAPER
        )

        db.commit()

        return {
            "listing_id": listing.id,
            "hotel_id": provider.id,
            "hotel_name": provider.name,
            "room_name": listing.name,
            "price_per_night": listing.price,
            "action": action,
            "validation_warnings": warnings
        }


hotels_service = HotelsService()
