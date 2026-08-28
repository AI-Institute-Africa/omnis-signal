"""
Telecom Service — Manages 8 mobile data and telecom bundle categories,
6-field shared schema validation, operator enum normalisation, price_per_gb calculation,
and automated bundle ingestion.
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


CANONICAL_OPERATORS = {
    "econet": "Econet",
    "econet wireless": "Econet",
    "econet wireless zimbabwe": "Econet",
    "netone": "NetOne",
    "netone cellular": "NetOne",
    "net one": "NetOne",
    "telecel": "Telecel",
    "telecel zimbabwe": "Telecel"
}

TELECOM_CATEGORY_SLUGS = [
    "whatsapp-data",
    "private-wifi",
    "general-data",
    "sms",
    "voice-bundle",
    "big-beautiful-bundles",
    "social-media-bundles",
    "freedom-bundles"
]


class TelecomService:
    @staticmethod
    def get_telecom_sector(db: Session) -> SectorConfig:
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "telecom").first()
        if not sector:
            raise ValueError("Telecom sector not found in database.")
        return sector

    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """Returns all 8 telecom categories with their 6-field attribute schema."""
        sector = TelecomService.get_telecom_sector(db)
        cats = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug.in_(TELECOM_CATEGORY_SLUGS)
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
    def get_bundles(
        db: Session,
        category_slug: Optional[str] = None,
        operator: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns telecom bundle listings with category and operator details."""
        sector = TelecomService.get_telecom_sector(db)
        q = db.query(Listing).join(Category, Listing.category_id == Category.id)
        q = q.filter(Category.sector_id == sector.id)

        if category_slug:
            q = q.filter(Category.slug == category_slug)

        listings = q.all()
        bundles = []
        for l in listings:
            p = l.provider
            c = l.category
            attrs = l.attributes or {}

            if operator:
                norm_op = TelecomService.normalise_operator(operator)
                if attrs.get("operator") != norm_op and (p and p.name != norm_op):
                    continue

            bundles.append({
                "listing_id": l.id,
                "operator_id": p.id if p else l.provider_id,
                "operator": attrs.get("operator") or (p.name if p else l.name),
                "category_slug": c.slug if c else None,
                "category_name": c.name if c else None,
                "bundle_name": attrs.get("bundle_name") or l.name,
                "listing_name": l.name,
                "price": l.price,
                "currency": l.currency,
                "validity": attrs.get("validity"),
                "benefit": attrs.get("benefit"),
                "data_mb": attrs.get("data_mb"),
                "price_per_gb": attrs.get("price_per_gb"),
                "source_url": l.source_url or (p.website_url if p else None),
                "last_verified_at": l.last_verified_at.isoformat() if l.last_verified_at else None
            })

        return bundles

    @staticmethod
    def normalise_operator(val: Optional[str]) -> str:
        if not val:
            return "Econet"
        cleaned = str(val).strip().lower()
        return CANONICAL_OPERATORS.get(cleaned, "Econet")

    @staticmethod
    def parse_data_mb(val: Any) -> float:
        """Parse data allowance string or number to MB (e.g. '1GB' -> 1000, '500MB' -> 500)."""
        if isinstance(val, (int, float)):
            return float(val)
        if not val:
            return 0.0
        s = str(val).strip().upper()
        m_gb = re.search(r"(\d+(?:\.\d+)?)\s*GB", s)
        if m_gb:
            return float(m_gb.group(1)) * 1000.0
        m_mb = re.search(r"(\d+(?:\.\d+)?)\s*MB", s)
        if m_mb:
            return float(m_mb.group(1))
        m_num = re.search(r"(\d+(?:\.\d+)?)", s)
        if m_num:
            return float(m_num.group(1))
        return 0.0

    @staticmethod
    def compute_price_per_gb(price: float, data_mb: float) -> float:
        """Compute price per GB in USD (price / (data_mb / 1000.0))."""
        if data_mb <= 0 or price <= 0:
            return 0.0
        gb = data_mb / 1000.0
        return round(price / gb, 2)

    @staticmethod
    def ingest_bundle_listing(
        db: Session,
        operator_name: str,
        category_slug: str,
        bundle_name: str,
        price: float,
        currency: str = "USD",
        attributes: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Direct DB write ingestion for a telecom bundle listing.
        Normalises operator, parses data_mb, and computes price_per_gb.
        """
        sector = TelecomService.get_telecom_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == category_slug
        ).first()

        if not cat:
            raise ValueError(f"Category '{category_slug}' not found under Telecom sector.")

        attrs = attributes.copy() if attributes else {}

        # 1. Normalise operator
        raw_op = attrs.get("operator") or operator_name
        norm_op = TelecomService.normalise_operator(raw_op)
        attrs["operator"] = norm_op

        # 2. Bundle Name
        if "bundle_name" not in attrs:
            attrs["bundle_name"] = bundle_name

        # 3. Parse data_mb
        data_mb = TelecomService.parse_data_mb(attrs.get("data_mb", 0))
        attrs["data_mb"] = data_mb

        # 4. Compute price_per_gb if not provided or 0
        if "price_per_gb" not in attrs or attrs["price_per_gb"] is None:
            attrs["price_per_gb"] = TelecomService.compute_price_per_gb(float(price), data_mb)
        else:
            attrs["price_per_gb"] = round(float(attrs["price_per_gb"]), 2)

        # Set default benefit & validity if missing
        if "validity" not in attrs:
            attrs["validity"] = "30 days"
        if "benefit" not in attrs:
            attrs["benefit"] = f"{int(data_mb)}MB" if data_mb > 0 else bundle_name

        provider = get_or_create_provider(db, name=norm_op, source_url=source_url)
        warnings = validate_attributes(db, cat.id, attrs)

        listing, action = upsert_listing(
            db,
            category_id=cat.id,
            provider_id=provider.id,
            name=bundle_name,
            price=float(price),
            currency=currency,
            attributes=attrs,
            source_url=source_url,
            description=description or f"{attrs.get('benefit', '')}, {attrs.get('validity', '')} validity",
            status=ListingStatus.PUBLISHED,
            freshness_status=FreshnessStatus.UNVERIFIED,
            last_update_source=ListingUpdateSource.SCRAPER
        )

        db.commit()

        return {
            "listing_id": listing.id,
            "operator": norm_op,
            "category_slug": cat.slug,
            "bundle_name": listing.name,
            "price": listing.price,
            "data_mb": data_mb,
            "price_per_gb": attrs.get("price_per_gb"),
            "action": action,
            "validation_warnings": warnings
        }


telecom_service = TelecomService()
