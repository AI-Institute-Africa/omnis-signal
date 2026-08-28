"""
Retail & Groceries Service — Manages 25 retail commodity categories,
common 12-field schema validation, unit-price computation, and automated listing ingestion.
"""
import re
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


class RetailService:
    @staticmethod
    def get_retail_sector(db: Session) -> SectorConfig:
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "retail").first()
        if not sector:
            raise ValueError("Retail & Groceries sector not found in database.")
        return sector

    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """Returns all 25 retail categories with their 12-field attribute schema."""
        sector = RetailService.get_retail_sector(db)
        slugs = [
            "cooking-oil", "maize-meal-roller-meal", "rice", "sugar", "bread",
            "milk", "chicken", "eggs", "cement", "solar-panel", "inverter",
            "wheat-flour", "salt", "soya-chunks", "groundnuts-peanuts",
            "toothbrushes", "ibr-roofing", "maize-grain", "pasta-spaghetti",
            "dried-beans-sugar-beans", "beef", "tomatoes", "matches",
            "goat-meat-chevon", "beef-offal"
        ]
        cats = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug.in_(slugs)
        ).all()

        results = []
        for c in cats:
            c_dict = c.to_dict()
            fields = db.query(AttributeSchemaField).filter(
                AttributeSchemaField.category_id == c.id
            ).order_by(AttributeSchemaField.sort_order).all()
            c_dict["schema_fields"] = [f.to_dict() for f in fields]
            results.append(c_dict)

        return sorted(results, key=lambda x: x["name"])

    @staticmethod
    def get_products(
        db: Session,
        category_slug: Optional[str] = None,
        brand: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns retail commodity listings with category and provider details."""
        sector = RetailService.get_retail_sector(db)
        q = db.query(Listing).join(Category, Listing.category_id == Category.id)
        q = q.filter(Category.sector_id == sector.id)

        if category_slug:
            q = q.filter(Category.slug == category_slug)

        listings = q.all()
        products = []
        for l in listings:
            p = l.provider
            c = l.category
            attrs = l.attributes or {}

            if brand and attrs.get("brand", "").lower() != brand.lower():
                continue

            products.append({
                "listing_id": l.id,
                "provider_id": p.id if p else l.provider_id,
                "provider_name": p.name if p else l.name,
                "category_slug": c.slug if c else None,
                "category_name": c.name if c else None,
                "product_name": l.name,
                "shelf_price": l.price,
                "currency": l.currency,
                "unit_price_usd": attrs.get("unit_price_usd"),
                "pack_size": attrs.get("pack_size"),
                "brand": attrs.get("brand"),
                "origin": attrs.get("origin"),
                "local_or_import": attrs.get("local_or_import"),
                "counterfeit_risk_level": attrs.get("counterfeit_risk_level"),
                "quality_tier": attrs.get("quality_tier"),
                "zesa_survival": attrs.get("zesa_survival"),
                "storage_life": attrs.get("storage_life"),
                "seasonality": attrs.get("seasonality"),
                "where_to_buy": attrs.get("where_to_buy"),
                "price_source": attrs.get("price_source"),
                "source_url": l.source_url or (p.website_url if p else None),
                "last_verified_at": l.last_verified_at.isoformat() if l.last_verified_at else None
            })

        return products

    @staticmethod
    def compute_unit_price(shelf_price: float, pack_size: Optional[str]) -> float:
        """
        Computes the normalised per-kg / per-litre / per-watt price from shelf price and pack size string.
        Examples:
          "2L" -> 2.0 -> shelf_price / 2.0
          "10kg" -> 10.0 -> shelf_price / 10.0
          "700g" -> 0.7 -> shelf_price / 0.7
          "500ml" -> 0.5 -> shelf_price / 0.5
          "550W" -> 550.0 -> shelf_price / 550.0
          "tray of 30" -> 30.0 -> shelf_price / 30.0
        """
        if not pack_size or shelf_price <= 0:
            return round(shelf_price, 2)

        s = pack_size.lower().strip()

        # Grams e.g. 500g, 750g
        m_g = re.search(r"(\d+(?:\.\d+)?)\s*g\b", s)
        if m_g:
            g = float(m_g.group(1))
            if g > 0:
                kg = g / 1000.0
                return round(shelf_price / kg, 2)

        # Millilitres e.g. 500ml, 750ml
        m_ml = re.search(r"(\d+(?:\.\d+)?)\s*ml\b", s)
        if m_ml:
            ml = float(m_ml.group(1))
            if ml > 0:
                l = ml / 1000.0
                return round(shelf_price / l, 2)

        # Kilograms / Litres / Watts / Counts
        m_num = re.search(r"(\d+(?:\.\d+)?)", s)
        if m_num:
            val = float(m_num.group(1))
            if val > 0:
                return round(shelf_price / val, 2)

        return round(shelf_price, 2)

    @staticmethod
    def ingest_product_listing(
        db: Session,
        supplier_name: str,
        category_slug: str,
        product_name: str,
        price: float,
        currency: str = "USD",
        attributes: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Direct DB write ingestion for a retail commodity product.
        Computes unit_price_usd if not provided, normalises local_or_import.
        """
        sector = RetailService.get_retail_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == category_slug
        ).first()

        if not cat:
            raise ValueError(f"Category '{category_slug}' not found under Retail & Groceries sector.")

        attrs = attributes.copy() if attributes else {}

        # 1. Compute unit_price_usd if missing
        if "unit_price_usd" not in attrs or attrs["unit_price_usd"] is None:
            pack_size = attrs.get("pack_size")
            attrs["unit_price_usd"] = RetailService.compute_unit_price(float(price), pack_size)
        else:
            attrs["unit_price_usd"] = round(float(attrs["unit_price_usd"]), 2)

        # 2. Normalise local_or_import
        if "local_or_import" in attrs:
            val = str(attrs["local_or_import"]).strip().lower()
            attrs["local_or_import"] = "import" if "import" in val else "local"

        # 3. Ensure price_source exists for auditability
        if "price_source" not in attrs:
            pack_size = attrs.get("pack_size", "")
            attrs["price_source"] = f"{currency} {price:.2f}" + (f" / {pack_size}" if pack_size else "")

        provider = get_or_create_provider(db, name=supplier_name, source_url=source_url)
        warnings = validate_attributes(db, cat.id, attrs)

        listing, action = upsert_listing(
            db,
            category_id=cat.id,
            provider_id=provider.id,
            name=product_name,
            price=float(price),
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
            "provider_id": provider.id,
            "provider_name": provider.name,
            "category_slug": cat.slug,
            "product_name": listing.name,
            "shelf_price": listing.price,
            "unit_price_usd": attrs.get("unit_price_usd"),
            "action": action,
            "validation_warnings": warnings
        }


retail_service = RetailService()
