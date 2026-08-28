"""
Transport Service — Manages 8 transport categories, 16-field shared schema validation,
ownership/urbanicity/freight enum normalisations, and automated fare ingestion.
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


OWNERSHIP_STATUS_CANONICAL = {
    "state": "state",
    "public": "state",
    "government": "state",
    "parastatal": "state",
    "zupco": "state",
    "private": "private",
    "cooperative": "cooperative",
    "coop": "cooperative",
    "association": "cooperative",
    "franchise": "franchise",
    "zupco franchise": "franchise"
}

URBANICITY_CANONICAL = {
    "urban": "urban",
    "city": "urban",
    "metro": "urban",
    "rural": "rural",
    "village": "rural",
    "growth point": "rural",
    "both": "both",
    "intercity": "both",
    "cross-border": "both"
}

PASSENGER_FREIGHT_CANONICAL = {
    "passenger": "passenger",
    "people": "passenger",
    "commuter": "passenger",
    "freight": "freight",
    "cargo": "freight",
    "haulage": "freight",
    "both": "both"
}

TRANSPORT_CATEGORY_SLUGS = [
    "urban-commuter",
    "intercity",
    "freight-cargo",
    "cross-border",
    "rural",
    "air",
    "last-mile",
    "contract-staff"
]


class TransportService:
    @staticmethod
    def get_transport_sector(db: Session) -> SectorConfig:
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "transport").first()
        if not sector:
            raise ValueError("Transport sector not found in database.")
        return sector

    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """Returns all 8 transport categories with their 16-field attribute schema."""
        sector = TransportService.get_transport_sector(db)
        cats = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug.in_(TRANSPORT_CATEGORY_SLUGS)
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
    def get_services(
        db: Session,
        category_slug: Optional[str] = None,
        province_district: Optional[str] = None,
        ownership_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns transport services, routes, and fare listings."""
        sector = TransportService.get_transport_sector(db)
        q = db.query(Listing).join(Category, Listing.category_id == Category.id)
        q = q.filter(Category.sector_id == sector.id)

        if category_slug:
            q = q.filter(Category.slug == category_slug)

        listings = q.all()
        services = []
        for l in listings:
            p = l.provider
            c = l.category
            attrs = l.attributes or {}

            if province_district and province_district.lower() not in attrs.get("province_district", "").lower():
                continue

            if ownership_status and attrs.get("ownership_status", "").lower() != ownership_status.lower():
                continue

            services.append({
                "listing_id": l.id,
                "operator_id": p.id if p else l.provider_id,
                "operator_name": p.name if p else l.name,
                "category_slug": c.slug if c else None,
                "category_name": c.name if c else None,
                "service_name": l.name,
                "fare": l.price,
                "fare_gazetted": attrs.get("fare_gazetted"),
                "fare_estimate": attrs.get("fare_estimate"),
                "currency": l.currency,
                "service_level": attrs.get("service_level"),
                "fleet_type": attrs.get("fleet_type"),
                "province_district": attrs.get("province_district"),
                "ownership_status": attrs.get("ownership_status"),
                "urbanicity": attrs.get("urbanicity"),
                "passenger_or_freight": attrs.get("passenger_or_freight"),
                "punctuality_score": attrs.get("punctuality_score"),
                "comfort_score": attrs.get("comfort_score"),
                "safety_score": attrs.get("safety_score"),
                "coverage_score": attrs.get("coverage_score"),
                "reliability_score": attrs.get("reliability_score"),
                "source_url": l.source_url or (p.website_url if p else None),
                "last_verified_at": l.last_verified_at.isoformat() if l.last_verified_at else None
            })

        return services

    @staticmethod
    def normalise_ownership_status(val: Optional[str]) -> str:
        if not val:
            return "private"
        cleaned = str(val).strip().lower()
        return OWNERSHIP_STATUS_CANONICAL.get(cleaned, "private")

    @staticmethod
    def normalise_urbanicity(val: Optional[str]) -> str:
        if not val:
            return "urban"
        cleaned = str(val).strip().lower()
        return URBANICITY_CANONICAL.get(cleaned, "urban")

    @staticmethod
    def normalise_passenger_or_freight(val: Optional[str]) -> str:
        if not val:
            return "passenger"
        cleaned = str(val).strip().lower()
        return PASSENGER_FREIGHT_CANONICAL.get(cleaned, "passenger")

    @staticmethod
    def ingest_transport_listing(
        db: Session,
        operator_name: str,
        category_slug: str,
        service_name: str,
        fare_gazetted: Optional[float] = None,
        fare_estimate: Optional[float] = None,
        price: Optional[float] = None,
        currency: str = "USD",
        attributes: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Direct DB write ingestion for a transport operator / route listing.
        Authoritative price is fare_gazetted when available, else fare_estimate.
        """
        sector = TransportService.get_transport_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == category_slug
        ).first()

        if not cat:
            raise ValueError(f"Category '{category_slug}' not found under Transport sector.")

        attrs = attributes.copy() if attributes else {}

        # 1. Fare mapping & Authoritative price determination
        gazetted = fare_gazetted if fare_gazetted is not None else attrs.get("fare_gazetted")
        estimate = fare_estimate if fare_estimate is not None else attrs.get("fare_estimate")

        if gazetted is not None:
            gazetted = float(gazetted)
            attrs["fare_gazetted"] = gazetted
        if estimate is not None:
            estimate = float(estimate)
            attrs["fare_estimate"] = estimate

        if price is not None:
            final_price = float(price)
        elif gazetted is not None:
            final_price = float(gazetted)
        elif estimate is not None:
            final_price = float(estimate)
        else:
            final_price = 0.0

        # 2. Normalise enums
        if "ownership_status" in attrs:
            attrs["ownership_status"] = TransportService.normalise_ownership_status(attrs["ownership_status"])
        if "urbanicity" in attrs:
            attrs["urbanicity"] = TransportService.normalise_urbanicity(attrs["urbanicity"])
        if "passenger_or_freight" in attrs:
            attrs["passenger_or_freight"] = TransportService.normalise_passenger_or_freight(attrs["passenger_or_freight"])

        # 3. Quality scores 1-5 (do not invent — leave None if not provided)
        for score_key in ("punctuality_score", "comfort_score", "safety_score", "coverage_score", "reliability_score"):
            if score_key in attrs and attrs[score_key] is not None:
                attrs[score_key] = round(float(attrs[score_key]), 1)

        provider = get_or_create_provider(db, name=operator_name, source_url=source_url)
        warnings = validate_attributes(db, cat.id, attrs)

        listing, action = upsert_listing(
            db,
            category_id=cat.id,
            provider_id=provider.id,
            name=service_name,
            price=final_price,
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
            "operator_name": provider.name,
            "category_slug": cat.slug,
            "service_name": listing.name,
            "fare": listing.price,
            "fare_gazetted": gazetted,
            "fare_estimate": estimate,
            "action": action,
            "validation_warnings": warnings
        }


transport_service = TransportService()
