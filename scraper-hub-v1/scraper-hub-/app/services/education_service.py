"""
Education Service — Manages institutions (schools and universities),
education category schemas, enum normalisation, and automated tuition fee ingestion.
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


CANONICAL_CURRICULUMS = {
    "zimbabwe": "Zimbabwe",
    "moesac": "Zimbabwe",
    "zimsec": "Zimbabwe",
    "cambridge": "Cambridge",
    "cie": "Cambridge",
    "ib": "IB",
    "international baccalaureate": "IB",
    "other": "other"
}

CANONICAL_STUDY_MODES = {
    "full_time": "full_time",
    "full time": "full_time",
    "fulltime": "full_time",
    "part_time": "part_time",
    "part time": "part_time",
    "parttime": "part_time",
    "distance": "distance",
    "distance learning": "distance",
    "online": "distance",
    "blended": "blended",
    "hybrid": "blended",
    "block release": "blended"
}


class EducationService:
    @staticmethod
    def get_education_sector(db: Session) -> SectorConfig:
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "education").first()
        if not sector:
            raise ValueError("Education sector not found in database.")
        return sector

    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """Returns the 3 education categories with their attribute schemas."""
        sector = EducationService.get_education_sector(db)
        cats = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug.in_(["primary-schools", "secondary-schools", "universities"])
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
    def get_institutions(db: Session, category_slug: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns list of educational institutions and their listings."""
        sector = EducationService.get_education_sector(db)
        q = db.query(Listing).join(Category, Listing.category_id == Category.id)
        q = q.filter(Category.sector_id == sector.id)

        if category_slug:
            q = q.filter(Category.slug == category_slug)

        listings = q.all()
        institutions = []
        for l in listings:
            p = l.provider
            c = l.category
            institutions.append({
                "listing_id": l.id,
                "institution_id": p.id if p else l.provider_id,
                "institution_name": p.name if p else l.name,
                "category_slug": c.slug if c else None,
                "category_name": c.name if c else None,
                "program_name": l.name,
                "price": l.price,
                "currency": l.currency,
                "attributes": l.attributes or {},
                "website_url": l.source_url or (p.website_url if p else None),
                "corporate_domain": p.corporate_domain if p else None,
                "last_verified_at": l.last_verified_at.isoformat() if l.last_verified_at else None
            })

        return institutions

    @staticmethod
    def normalise_curriculum(val: Optional[str]) -> str:
        if not val:
            return "other"
        cleaned = str(val).strip().lower()
        return CANONICAL_CURRICULUMS.get(cleaned, "other")

    @staticmethod
    def normalise_study_mode(val: Optional[str]) -> str:
        if not val:
            return "full_time"
        cleaned = str(val).strip().lower()
        return CANONICAL_STUDY_MODES.get(cleaned, "full_time")

    @staticmethod
    def ingest_listing(
        db: Session,
        institution_name: str,
        category_slug: str,
        listing_name: str,
        price: float,
        currency: str = "USD",
        attributes: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Direct DB write ingestion for an education institution listing.
        Handles curriculum & study mode normalisation.
        """
        sector = EducationService.get_education_sector(db)
        cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == category_slug
        ).first()

        if not cat:
            raise ValueError(f"Category '{category_slug}' not found under Education sector.")

        attrs = attributes.copy() if attributes else {}

        # Enum normalisation
        if "curriculum" in attrs:
            attrs["curriculum"] = EducationService.normalise_curriculum(attrs["curriculum"])
        if "study_mode" in attrs:
            attrs["study_mode"] = EducationService.normalise_study_mode(attrs["study_mode"])

        # Sync price with attribute if not passed
        if category_slug in ("primary-schools", "secondary-schools"):
            if "term_fees" in attrs:
                price = float(attrs["term_fees"])
            else:
                attrs["term_fees"] = float(price)
        elif category_slug == "universities":
            if "tuition_per_year" in attrs:
                price = float(attrs["tuition_per_year"])
            else:
                attrs["tuition_per_year"] = float(price)

        provider = get_or_create_provider(db, name=institution_name, source_url=source_url)
        warnings = validate_attributes(db, cat.id, attrs)

        listing, action = upsert_listing(
            db,
            category_id=cat.id,
            provider_id=provider.id,
            name=listing_name,
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
            "institution_id": provider.id,
            "institution_name": provider.name,
            "category_slug": cat.slug,
            "listing_name": listing.name,
            "price": listing.price,
            "action": action,
            "validation_warnings": warnings
        }


education_service = EducationService()
