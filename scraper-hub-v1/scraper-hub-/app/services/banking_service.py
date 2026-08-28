"""
Banking Service — Manages the 3-level banking fee hierarchy, bank provider directory,
channel matrix, and automated fee scraper ingestion.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.models.catalog import (
    SectorConfig, Category, AttributeSchemaField, Provider,
    Listing, ListingPriceHistory,
    SectorStatus, CategoryLevel, ListingStatus, FreshnessStatus, ListingUpdateSource
)
from app.services.catalog_service import (
    get_sector_by_slug,
    get_or_create_provider,
    upsert_listing,
    validate_attributes
)


class BankingService:
    @staticmethod
    def get_banking_sector(db: Session) -> SectorConfig:
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "banking").first()
        if not sector:
            raise ValueError("Banking sector not found in database.")
        return sector

    @staticmethod
    def get_fee_hierarchy(db: Session) -> List[Dict[str, Any]]:
        """
        Returns the full 3-level nested banking fee hierarchy tree:
        Level 1: Fee Category (parent_id = None)
          └── Level 2: Subcategory (parent_id = fee_category.id)
                └── Level 3: Revenue Line (parent_id = subcategory.id, channel = ...)
                      └── Attribute Schema Fields
        """
        sector = BankingService.get_banking_sector(db)

        # 1. Fetch all fee categories (Level 1)
        fee_categories = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.level == CategoryLevel.FEE_CATEGORY
        ).all()

        tree = []
        for fc in fee_categories:
            fc_dict = fc.to_dict()
            fc_dict["subcategories"] = []

            # 2. Fetch subcategories for this fee_category (Level 2)
            subcategories = db.query(Category).filter(
                Category.sector_id == sector.id,
                Category.level == CategoryLevel.SUBCATEGORY,
                Category.parent_id == fc.id
            ).all()

            for sc in subcategories:
                sc_dict = sc.to_dict()
                sc_dict["revenue_lines"] = []

                # 3. Fetch revenue lines for this subcategory (Level 3)
                revenue_lines = db.query(Category).filter(
                    Category.sector_id == sector.id,
                    Category.level == CategoryLevel.REVENUE_LINE,
                    Category.parent_id == sc.id
                ).all()

                for rl in revenue_lines:
                    rl_dict = rl.to_dict()
                    fields = db.query(AttributeSchemaField).filter(
                        AttributeSchemaField.category_id == rl.id
                    ).order_by(AttributeSchemaField.sort_order).all()

                    rl_dict["schema_fields"] = [f.to_dict() for f in fields]
                    sc_dict["revenue_lines"].append(rl_dict)

                fc_dict["subcategories"].append(sc_dict)

            tree.append(fc_dict)

        return tree

    @staticmethod
    def get_flat_categories(db: Session) -> List[Dict[str, Any]]:
        """Returns the 4 flat consumer banking categories with their schema fields."""
        sector = BankingService.get_banking_sector(db)
        flat_slugs = ["savings-accounts", "current-accounts", "nostro-fca-accounts", "banks"]
        cats = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug.in_(flat_slugs)
        ).all()

        results = []
        for c in cats:
            c_dict = c.to_dict()
            fields = db.query(AttributeSchemaField).filter(
                AttributeSchemaField.category_id == c.id
            ).order_by(AttributeSchemaField.sort_order).all()
            c_dict["schema_fields"] = [f.to_dict() for f in fields]
            results.append(c_dict)

        return results

    @staticmethod
    def get_banks_directory(db: Session) -> List[Dict[str, Any]]:
        """
        Returns all 23 banks with their channel capabilities, USSD codes,
        and directory listings under the 'banks' category.
        """
        sector = BankingService.get_banking_sector(db)
        banks_cat = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == "banks"
        ).first()

        if not banks_cat:
            return []

        listings = db.query(Listing).filter(
            Listing.category_id == banks_cat.id
        ).all()

        directory = []
        for l in listings:
            p = l.provider
            attrs = l.attributes or {}
            directory.append({
                "provider_id": p.id if p else l.provider_id,
                "bank_name": p.name if p else l.name,
                "corporate_domain": p.corporate_domain if p else None,
                "website_url": l.source_url or (p.website_url if p else None),
                "bank_type": attrs.get("bank_type"),
                "ussd_code": attrs.get("ussd_code"),
                "ussd_brand": attrs.get("ussd_brand"),
                "channel_count": attrs.get("channel_count", 0),
                "channels": {
                    "mobile_app": attrs.get("channel_mobile_app", False),
                    "internet_banking": attrs.get("channel_internet", False),
                    "whatsapp_banking": attrs.get("channel_whatsapp", False),
                    "agency_banking": attrs.get("channel_agency", False),
                    "branch_banking": attrs.get("channel_branch", False),
                    "atm_network": attrs.get("channel_atm", False),
                    "pos_services": attrs.get("channel_pos", False),
                    "zipit_enabled": attrs.get("channel_zipit", False),
                    "wallet_link": attrs.get("channel_wallet_link", False),
                    "call_centre": attrs.get("channel_call_centre", False),
                },
                "last_verified_at": l.last_verified_at.isoformat() if l.last_verified_at else None
            })

        return sorted(directory, key=lambda x: x["bank_name"])

    @staticmethod
    def ingest_fee(
        db: Session,
        bank_name: str,
        revenue_line_slug: str,
        listing_name: str,
        price: float,
        currency: str = "USD",
        attributes: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a banking fee or rate into a specific revenue line.
        Ensures target category is a valid revenue_line in the banking hierarchy.
        """
        sector = BankingService.get_banking_sector(db)
        revenue_line = db.query(Category).filter(
            Category.sector_id == sector.id,
            Category.slug == revenue_line_slug,
            Category.level == CategoryLevel.REVENUE_LINE
        ).first()

        if not revenue_line:
            raise ValueError(f"Revenue line '{revenue_line_slug}' not found in banking fee hierarchy.")

        provider = get_or_create_provider(db, name=bank_name, source_url=source_url)
        attrs = attributes or {}
        warnings = validate_attributes(db, revenue_line.id, attrs)

        listing, action = upsert_listing(
            db,
            category_id=revenue_line.id,
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
            "bank_name": provider.name,
            "revenue_line": revenue_line.name,
            "revenue_line_slug": revenue_line.slug,
            "channel": revenue_line.channel,
            "action": action,
            "validation_warnings": warnings
        }


banking_service = BankingService()
