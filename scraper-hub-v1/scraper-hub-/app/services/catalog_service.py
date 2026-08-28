"""
Catalog service providing business logic for resolving sectors, categories,
providers, attributes validation, and idempotent listing upserts with price snapshots.
"""
import re
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.db.models.catalog import (
    SectorConfig, Category, AttributeSchemaField, Provider,
    Listing, ListingPriceHistory,
    SectorStatus, ListingStatus, FreshnessStatus, ListingUpdateSource, AttributeDataType
)


def _uid() -> str:
    return str(uuid.uuid4())


def normalise_provider_name(name: str) -> str:
    """Normalise company name (e.g. 'CBZ Bank Limited' -> 'CBZ Bank')."""
    if not name:
        return ""
    cleaned = name.strip()
    patterns = [
        r'(?i)\s+(plc|pbc|ltd|limited|holdings|group|corporation|inc)\.?$',
    ]
    for pat in patterns:
        cleaned = re.sub(pat, '', cleaned).strip()
    return cleaned


def get_sector_by_slug(db: Session, slug: str) -> Optional[SectorConfig]:
    """Look up a sector by slug. Raises ValueError if coming_soon."""
    sector = db.query(SectorConfig).filter(SectorConfig.slug == slug).first()
    if not sector:
        return None
    if sector.status == SectorStatus.COMING_SOON:
        raise ValueError(f"Sector '{slug}' is coming_soon and cannot accept listings.")
    return sector


def get_category_by_slug(db: Session, sector_id: str, slug: str) -> Optional[Category]:
    """Look up a category by slug scoped to sector_id."""
    return db.query(Category).filter(
        Category.sector_id == sector_id,
        Category.slug == slug
    ).first()


def get_or_create_provider(
    db: Session,
    name: str,
    website_url: Optional[str] = None,
    logo_url: Optional[str] = None,
    corporate_domain: Optional[str] = None,
    description: Optional[str] = None,
    source_url: Optional[str] = None
) -> Provider:
    """Resolve or create a provider by canonicalised name."""
    canonical = normalise_provider_name(name)
    if not canonical:
        raise ValueError("Provider name cannot be empty.")

    provider = db.query(Provider).filter(
        (Provider.name == canonical) | (Provider.name == name.strip())
    ).first()

    if not provider:
        provider = Provider(
            id=_uid(),
            name=canonical,
            website_url=website_url or source_url,
            logo_url=logo_url,
            corporate_domain=corporate_domain,
            description=description,
            verified=True,
        )
        db.add(provider)
        db.flush()

    return provider


def validate_attributes(db: Session, category_id: str, attributes: Dict[str, Any]) -> List[str]:
    """
    Validate listing attributes against the category schema.
    Returns a list of warning/error messages.
    """
    warnings = []
    schema_fields = db.query(AttributeSchemaField).filter(
        AttributeSchemaField.category_id == category_id
    ).all()

    schema_map = {f.key: f for f in schema_fields}

    for key, val in attributes.items():
        if key not in schema_map:
            warnings.append(f"Attribute '{key}' is not defined in category schema.")
            continue

        field = schema_map[key]
        if val is None:
            continue

        if field.data_type == AttributeDataType.NUMBER:
            if not isinstance(val, (int, float)):
                try:
                    float(str(val).replace('$', '').replace(',', '').strip())
                except (ValueError, TypeError):
                    warnings.append(f"Attribute '{key}' expects numeric value, got '{val}'.")

        elif field.data_type == AttributeDataType.BOOLEAN:
            if not isinstance(val, bool):
                if str(val).lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
                    warnings.append(f"Attribute '{key}' expects boolean value, got '{val}'.")

    return warnings


def upsert_listing(
    db: Session,
    category_id: str,
    provider_id: str,
    name: str,
    price: float,
    currency: str = "USD",
    attributes: Optional[Dict[str, Any]] = None,
    source_url: Optional[str] = None,
    description: Optional[str] = None,
    status: str = ListingStatus.PUBLISHED,
    freshness_status: str = FreshnessStatus.UNVERIFIED,
    last_update_source: str = ListingUpdateSource.SCRAPER,
) -> Tuple[Listing, str]:
    normalised_name = name.strip()
    now = datetime.utcnow()
    attrs = attributes or {}

    listing = db.query(Listing).filter(
        Listing.category_id == category_id,
        Listing.provider_id == provider_id,
        Listing.name == normalised_name
    ).first()

    if not listing:
        listing = Listing(
            id=_uid(),
            category_id=category_id,
            provider_id=provider_id,
            name=normalised_name,
            description=description,
            price=float(price),
            currency=currency.upper() if currency else "USD",
            source_url=source_url,
            status=status,
            freshness_status=freshness_status,
            last_update_source=last_update_source,
            last_verified_at=now,
        )
        listing.attributes = attrs
        db.add(listing)
        db.flush()

        hist = ListingPriceHistory(
            id=_uid(),
            listing_id=listing.id,
            price=float(price),
            currency=currency.upper() if currency else "USD",
            recorded_at=now,
        )
        db.add(hist)
        db.flush()
        return listing, "created"

    price_changed = abs(float(listing.price) - float(price)) > 0.0001
    action = "unchanged"

    if price_changed:
        old_hist = ListingPriceHistory(
            id=_uid(),
            listing_id=listing.id,
            price=float(listing.price),
            currency=listing.currency,
            recorded_at=now,
        )
        db.add(old_hist)
        listing.price = float(price)
        action = "updated"

    if description and listing.description != description:
        listing.description = description
        action = "updated"

    if source_url and listing.source_url != source_url:
        listing.source_url = source_url
        action = "updated"

    if attrs != listing.attributes:
        listing.attributes = attrs
        action = "updated"

    listing.last_verified_at = now
    listing.freshness_status = freshness_status
    listing.last_update_source = last_update_source
    db.flush()

    return listing, action
