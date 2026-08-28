"""
Food & Drink Service — Manages restaurant chains, outlets, menu categories,
attribute schemas, and automated food price / menu line ingestion.
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


class FoodService:
    @staticmethod
    def get_food_sector(db: Session) -> SectorConfig:
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "food").first()
        if not sector:
            raise ValueError("Food & Drink sector not found in database.")
        return sector

    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """Returns the 2 food categories (fast-food, casual-dining) with schemas."""
        sector = FoodService.get_food_sector(db)
        cats = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug.in_(["fast-food", "casual-dining"])
        ).all()

        results = []
        for c in cats:
            c_dict = c.to_dict()
            fields = db.query(AttributeSchemaField).filter(
                AttributeSchemaField.category_id == c.id
            ).order_by(AttributeSchemaField.sort_order).all()
            c_dict["schema_fields"] = [f.to_dict() for f in fields]
            results.append(c_dict)

        return sorted(results, key=lambda x: x["slug"])

    @staticmethod
    def get_restaurants(db: Session, category_slug: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns restaurants and their active menu listings."""
        sector = FoodService.get_food_sector(db)
        q = db.query(Listing).join(Category, Listing.category_id == Category.id)
        q = q.filter(Category.sector_id == sector.id)

        if category_slug:
            q = q.filter(Category.slug == category_slug)

        listings = q.all()
        menu_items = []
        for l in listings:
            p = l.provider
            c = l.category
            menu_items.append({
                "listing_id": l.id,
                "restaurant_id": p.id if p else l.provider_id,
                "restaurant_name": p.name if p else l.name,
                "category_slug": c.slug if c else None,
                "category_name": c.name if c else None,
                "menu_item_name": l.name,
                "price": l.price,
                "currency": l.currency,
                "attributes": l.attributes or {},
                "source_url": l.source_url or (p.website_url if p else None),
                "corporate_domain": p.corporate_domain if p else None,
                "last_verified_at": l.last_verified_at.isoformat() if l.last_verified_at else None
            })

        return menu_items

    @staticmethod
    def ingest_menu_item(
        db: Session,
        restaurant_name: str,
        category_slug: str,
        menu_item_name: str,
        price: float,
        currency: str = "USD",
        attributes: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Direct DB write ingestion for a restaurant menu item / meal offer.
        """
        sector = FoodService.get_food_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == category_slug
        ).first()

        if not cat:
            raise ValueError(f"Category '{category_slug}' not found under Food & Drink sector.")

        attrs = attributes.copy() if attributes else {}

        # Default attribute values based on category
        if category_slug == "fast-food" and "meal" not in attrs:
            attrs["meal"] = menu_item_name

        provider = get_or_create_provider(db, name=restaurant_name, source_url=source_url)
        warnings = validate_attributes(db, cat.id, attrs)

        listing, action = upsert_listing(
            db,
            category_id=cat.id,
            provider_id=provider.id,
            name=menu_item_name,
            price=price,
            currency=currency,
            attributes=attrs,
            source_url=source_url,
            description=description,
            status=ListingStatus.PUBLISHED,
            freshness_status=FreshnessStatus.UNVERIFIED,
            last_update_source=ListingUpdateSource.SCRAPER
        )

        db.commit()

        return {
            "listing_id": listing.id,
            "restaurant_id": provider.id,
            "restaurant_name": provider.name,
            "category_slug": cat.slug,
            "menu_item_name": listing.name,
            "price": listing.price,
            "action": action,
            "validation_warnings": warnings
        }


food_service = FoodService()
