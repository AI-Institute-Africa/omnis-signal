"""
Telecom Sector Database Seed
Implements:
1. Sector: telecom ("Telecom", status = live)
2. 8 Bundle Categories sharing the common 6-field attribute schema
3. Mobile Network Operators (Providers): Econet, NetOne, Telecel
4. Scrape Sources for Econet & NetOne
5. Sample mobile data, WhatsApp, voice, and freedom bundle listings
"""
import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.session import SessionLocal
from app.db.models.catalog import (
    SectorConfig, Category, AttributeSchemaField, Provider,
    Listing, ListingPriceHistory, ScrapeSource,
    SectorStatus, CategoryLevel, AttributeDataType, QualityAxis,
    ListingStatus, FreshnessStatus, ListingUpdateSource
)


def _uid() -> str:
    return str(uuid.uuid4())


# ============================================================================
# 1. SHARED 6-FIELD ATTRIBUTE SCHEMA SPECIFICATION
# ============================================================================
COMMON_TELECOM_FIELDS = [
    {"key": "operator", "label": "Network", "consumer_label": None, "data_type": AttributeDataType.ENUM, "unit": None, "quality_axis": None, "sort_order": 0},
    {"key": "bundle_name", "label": "Bundle", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 1},
    {"key": "validity", "label": "Validity", "consumer_label": "How long it lasts", "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 2},
    {"key": "benefit", "label": "What you get", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 3},
    {"key": "data_mb", "label": "Data allowance", "consumer_label": None, "data_type": AttributeDataType.NUMBER, "unit": "MB", "quality_axis": None, "sort_order": 4},
    {"key": "price_per_gb", "label": "Price per GB", "consumer_label": "Cost per GB", "data_type": AttributeDataType.NUMBER, "unit": "USD/GB", "quality_axis": None, "sort_order": 5},
]


# ============================================================================
# 2. ALL 8 TELECOM BUNDLE CATEGORIES
# ============================================================================
TELECOM_CATEGORIES = [
    {"slug": "whatsapp-data", "name": "WhatsApp Data", "synonyms": ["whatsapp bundle", "whatsapp data", "wa bundle"]},
    {"slug": "private-wifi", "name": "Private Wifi", "synonyms": ["wifi bundle", "private wifi", "home internet", "router bundle"]},
    {"slug": "general-data", "name": "General Data", "synonyms": ["data bundle", "internet bundle", "mobile data", "cheapest data"]},
    {"slug": "sms", "name": "SMS", "synonyms": ["sms bundle", "text bundle", "messages"]},
    {"slug": "voice-bundle", "name": "Voice Bundle", "synonyms": ["call bundle", "airtime bundle", "minutes", "talk time"]},
    {"slug": "big-beautiful-bundles", "name": "Big Beautiful Bundles", "synonyms": ["bbb", "big bundle", "combo bundle"]},
    {"slug": "social-media-bundles", "name": "Social Media Bundles", "synonyms": ["facebook bundle", "instagram bundle", "tiktok bundle", "social bundle"]},
    {"slug": "freedom-bundles", "name": "Freedom Bundles", "synonyms": ["freedom bundle", "netone freedom"]},
]


# ============================================================================
# 3. MOBILE NETWORK OPERATORS (PROVIDERS)
# ============================================================================
TELECOM_PROVIDERS = [
    {
        "name": "Econet",
        "website_url": "https://www.econet.co.zw/",
        "corporate_domain": "econet.co.zw",
        "description": "Leading mobile network operator and digital services provider in Zimbabwe"
    },
    {
        "name": "NetOne",
        "website_url": "https://www.netone.co.zw/",
        "corporate_domain": "netone.co.zw",
        "description": "National mobile telecommunications provider in Zimbabwe"
    },
    {
        "name": "Telecel",
        "website_url": "https://www.telecel.co.zw/",
        "corporate_domain": "telecel.co.zw",
        "description": "Telecommunications service provider in Zimbabwe"
    }
]


# ============================================================================
# 4. SAMPLE TELECOM BUNDLE LISTINGS
# ============================================================================
SAMPLE_TELECOM_LISTINGS = [
    # General Data - Econet
    {
        "operator": "Econet",
        "category_slug": "general-data",
        "name": "Econet 1GB Bundle",
        "price": 2.00,
        "source_url": "https://www.econet.co.zw/data/bundles/1gb",
        "description": "1GB data, 30 days validity",
        "attributes": {
            "operator": "Econet",
            "bundle_name": "1GB Bundle",
            "validity": "30 days",
            "benefit": "1GB data",
            "data_mb": 1000,
            "price_per_gb": 2.00
        }
    },
    {
        "operator": "Econet",
        "category_slug": "general-data",
        "name": "Econet 5GB Monthly Data",
        "price": 8.00,
        "source_url": "https://www.econet.co.zw/data/bundles/5gb",
        "description": "5GB standard internet data, 30 days validity",
        "attributes": {
            "operator": "Econet",
            "bundle_name": "5GB Monthly Data",
            "validity": "30 days",
            "benefit": "5GB high speed data",
            "data_mb": 5000,
            "price_per_gb": 1.60
        }
    },
    # General Data - NetOne
    {
        "operator": "NetOne",
        "category_slug": "general-data",
        "name": "NetOne 1GB Daily Data",
        "price": 1.50,
        "source_url": "https://www.netone.co.zw/data/daily",
        "description": "1GB 24-hour high-speed data",
        "attributes": {
            "operator": "NetOne",
            "bundle_name": "1GB Daily",
            "validity": "1 day",
            "benefit": "1GB data",
            "data_mb": 1000,
            "price_per_gb": 1.50
        }
    },
    # WhatsApp Data - Econet
    {
        "operator": "Econet",
        "category_slug": "whatsapp-data",
        "name": "Econet WhatsApp Weekly Bundle",
        "price": 1.20,
        "source_url": "https://www.econet.co.zw/bundles/whatsapp",
        "description": "Unlimited WhatsApp messaging and media for 7 days",
        "attributes": {
            "operator": "Econet",
            "bundle_name": "WhatsApp Weekly",
            "validity": "7 days",
            "benefit": "350MB WhatsApp data + calls",
            "data_mb": 350,
            "price_per_gb": 3.43
        }
    },
    # WhatsApp Data - NetOne
    {
        "operator": "NetOne",
        "category_slug": "whatsapp-data",
        "name": "NetOne WhatsApp Monthly Bundle",
        "price": 3.00,
        "source_url": "https://www.netone.co.zw/bundles/whatsapp",
        "description": "WhatsApp data bundle for 30 days",
        "attributes": {
            "operator": "NetOne",
            "bundle_name": "WhatsApp Monthly",
            "validity": "30 days",
            "benefit": "1000MB WhatsApp",
            "data_mb": 1000,
            "price_per_gb": 3.00
        }
    },
    # Private Wifi - Econet
    {
        "operator": "Econet",
        "category_slug": "private-wifi",
        "name": "Econet SmartHome 25GB Private WiFi",
        "price": 20.00,
        "source_url": "https://www.econet.co.zw/wifi/smarthome",
        "description": "Home router wifi data bundle with 25GB allowance",
        "attributes": {
            "operator": "Econet",
            "bundle_name": "SmartHome 25GB",
            "validity": "30 days",
            "benefit": "25GB 4G LTE Home WiFi",
            "data_mb": 25000,
            "price_per_gb": 0.80
        }
    },
    # Voice Bundle - Econet
    {
        "operator": "Econet",
        "category_slug": "voice-bundle",
        "name": "Econet Voice 60 Minutes",
        "price": 2.50,
        "source_url": "https://www.econet.co.zw/voice",
        "description": "60 on-net and cross-net calling minutes",
        "attributes": {
            "operator": "Econet",
            "bundle_name": "Voice 60 Mins",
            "validity": "7 days",
            "benefit": "60 call minutes",
            "data_mb": 0,
            "price_per_gb": 0.00
        }
    },
    # Big Beautiful Bundles - NetOne
    {
        "operator": "NetOne",
        "category_slug": "big-beautiful-bundles",
        "name": "NetOne Big Beautiful Bundle 10GB",
        "price": 11.00,
        "source_url": "https://www.netone.co.zw/bundles/bbb",
        "description": "10GB data combo with free on-net voice minutes",
        "attributes": {
            "operator": "NetOne",
            "bundle_name": "BBB 10GB Combo",
            "validity": "30 days",
            "benefit": "10GB data + 50 on-net mins",
            "data_mb": 10000,
            "price_per_gb": 1.10
        }
    },
    # Social Media Bundles - NetOne
    {
        "operator": "NetOne",
        "category_slug": "social-media-bundles",
        "name": "NetOne All-In-One Social Media Bundle",
        "price": 4.50,
        "source_url": "https://www.netone.co.zw/bundles/social",
        "description": "WhatsApp, Facebook, Instagram and Twitter 30-day access",
        "attributes": {
            "operator": "NetOne",
            "bundle_name": "All-in-One Social 2GB",
            "validity": "30 days",
            "benefit": "2GB Social Media",
            "data_mb": 2000,
            "price_per_gb": 2.25
        }
    },
    # Freedom Bundles - NetOne
    {
        "operator": "NetOne",
        "category_slug": "freedom-bundles",
        "name": "NetOne Freedom 5GB No-Expiry Bundle",
        "price": 10.00,
        "source_url": "https://www.netone.co.zw/bundles/freedom",
        "description": "Data bundle with no validity expiration date",
        "attributes": {
            "operator": "NetOne",
            "bundle_name": "Freedom 5GB",
            "validity": "no expiry",
            "benefit": "5GB non-expiring data",
            "data_mb": 5000,
            "price_per_gb": 2.00
        }
    }
]


def seed_telecom_sector(db=None):
    """Seed Telecom sector, 8 bundle categories, 6-field schema, MNOs, and bundle listings."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        print("[Telecom Seed] Starting Telecom Sector database seed...")

        # 1. Ensure Telecom sector exists and is LIVE
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "telecom").first()
        if not sector:
            sector = SectorConfig(
                id=_uid(),
                name="Telecom",
                slug="telecom",
                status=SectorStatus.LIVE,
                icon="wifi",
                blurb="Compare mobile data bundles, WhatsApp packs, voice minutes and private WiFi across Econet, NetOne and Telecel"
            )
            db.add(sector)
            db.flush()
            print("  [+] Created Sector: Telecom")
        else:
            sector.name = "Telecom"
            sector.status = SectorStatus.LIVE
            db.flush()

        # 2. Seed All 8 Categories & 6-Field Attribute Schema
        cat_map = {}
        for cat_spec in TELECOM_CATEGORIES:
            cat = db.query(Category).filter(
                Category.sector_id == sector.id,
                Category.slug == cat_spec["slug"]
            ).first()

            if not cat:
                cat = Category(
                    id=_uid(),
                    sector_id=sector.id,
                    name=cat_spec["name"],
                    slug=cat_spec["slug"],
                    level=CategoryLevel.STANDARD,
                    parent_id=None,
                    channel=None
                )
                cat.synonyms = cat_spec.get("synonyms", [])
                db.add(cat)
                db.flush()
                print(f"  [+] Category: {cat.name} ({cat.slug})")
            else:
                cat.synonyms = cat_spec.get("synonyms", [])
                cat.level = CategoryLevel.STANDARD

            cat_map[cat_spec["slug"]] = cat

            # Upsert all 6 schema fields for this category
            for f in COMMON_TELECOM_FIELDS:
                attr = db.query(AttributeSchemaField).filter(
                    AttributeSchemaField.category_id == cat.id,
                    AttributeSchemaField.key == f["key"]
                ).first()

                if not attr:
                    attr = AttributeSchemaField(
                        id=_uid(),
                        category_id=cat.id,
                        key=f["key"],
                        label=f["label"],
                        consumer_label=f.get("consumer_label"),
                        data_type=f["data_type"],
                        unit=f.get("unit"),
                        sort_order=f.get("sort_order", 0),
                        quality_axis=None,
                        is_comparable=True
                    )
                    db.add(attr)
                else:
                    attr.label = f["label"]
                    attr.consumer_label = f.get("consumer_label")
                    attr.data_type = f["data_type"]
                    attr.unit = f.get("unit")
                    attr.sort_order = f.get("sort_order", 0)
                    attr.quality_axis = None
                    attr.is_comparable = True

        # 3. Seed MNO Providers (Econet, NetOne, Telecel)
        provider_map = {}
        for p_data in TELECOM_PROVIDERS:
            provider = db.query(Provider).filter(Provider.name == p_data["name"]).first()
            if not provider:
                provider = Provider(
                    id=_uid(),
                    name=p_data["name"],
                    website_url=p_data.get("website_url"),
                    corporate_domain=p_data.get("corporate_domain"),
                    description=p_data.get("description"),
                    verified=True
                )
                db.add(provider)
                db.flush()
                print(f"  [+] Telecom Provider: {provider.name}")
            else:
                provider.website_url = p_data.get("website_url")
                provider.corporate_domain = p_data.get("corporate_domain")
                provider.description = p_data.get("description")
                db.flush()
            provider_map[p_data["name"]] = provider

        # 4. Seed Scrape Sources
        general_data_cat = cat_map.get("general-data")
        if general_data_cat:
            scrape_sources = [
                {"name": "Econet Zimbabwe", "url": "https://www.econet.co.zw/"},
                {"name": "NetOne Zimbabwe", "url": "https://www.netone.co.zw/"}
            ]
            for ss in scrape_sources:
                existing_ss = db.query(ScrapeSource).filter(
                    ScrapeSource.name == ss["name"]
                ).first()
                if not existing_ss:
                    src = ScrapeSource(
                        id=_uid(),
                        name=ss["name"],
                        url=ss["url"],
                        category_id=general_data_cat.id,
                        enabled=True
                    )
                    db.add(src)

        # 5. Seed Bundle Listings
        now = datetime.utcnow()
        for item in SAMPLE_TELECOM_LISTINGS:
            cat = cat_map.get(item["category_slug"])
            provider = provider_map.get(item["operator"])
            if not cat or not provider:
                continue

            listing = db.query(Listing).filter(
                Listing.category_id == cat.id,
                Listing.provider_id == provider.id,
                Listing.name == item["name"]
            ).first()

            if not listing:
                listing = Listing(
                    id=_uid(),
                    category_id=cat.id,
                    provider_id=provider.id,
                    name=item["name"],
                    description=item.get("description"),
                    price=float(item["price"]),
                    currency="USD",
                    source_url=item.get("source_url"),
                    status=ListingStatus.PUBLISHED,
                    freshness_status=FreshnessStatus.UNVERIFIED,
                    last_update_source=ListingUpdateSource.SCRAPER,
                    last_verified_at=now
                )
                listing.attributes = item.get("attributes", {})
                db.add(listing)
                db.flush()

                hist = ListingPriceHistory(
                    id=_uid(),
                    listing_id=listing.id,
                    price=float(item["price"]),
                    currency="USD",
                    recorded_at=now
                )
                db.add(hist)
            else:
                listing.price = float(item["price"])
                listing.attributes = item.get("attributes", {})
                listing.source_url = item.get("source_url")
                listing.last_verified_at = now

        db.commit()
        print(f"[Telecom Seed] Successfully seeded {len(TELECOM_CATEGORIES)} categories with 6-field schemas, MNOs, and bundle listings!")
    except Exception as e:
        db.rollback()
        print(f"[Telecom Seed] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_telecom_sector()
