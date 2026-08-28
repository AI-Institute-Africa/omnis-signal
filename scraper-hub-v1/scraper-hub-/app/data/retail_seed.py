"""
Retail & Groceries Sector Database Seed
Implements:
1. Sector: retail ("Retail & Groceries", status = live)
2. 25 Product Categories sharing the common 12-field attribute schema
3. Top retail providers / supermarkets / suppliers
4. Sample commodity listings with normalised unit prices
"""
import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.session import SessionLocal
from app.db.models.catalog import (
    SectorConfig, Category, AttributeSchemaField, Provider,
    Listing, ListingPriceHistory,
    SectorStatus, CategoryLevel, AttributeDataType, QualityAxis,
    ListingStatus, FreshnessStatus, ListingUpdateSource
)


def _uid() -> str:
    return str(uuid.uuid4())


# ============================================================================
# 1. COMMON 12-FIELD ATTRIBUTE SCHEMA SPECIFICATION
# ============================================================================
COMMON_RETAIL_FIELDS = [
    {"key": "brand", "label": "Brand", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 0},
    {"key": "pack_size", "label": "Pack size", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 1},
    {"key": "unit_price_usd", "label": "Unit price", "consumer_label": "Price per unit", "data_type": AttributeDataType.NUMBER, "unit": "USD", "quality_axis": None, "sort_order": 2},
    {"key": "counterfeit_risk_level", "label": "Counterfeit risk", "consumer_label": "Counterfeit risk (1 low - 4 very high)", "data_type": AttributeDataType.NUMBER, "unit": None, "quality_axis": QualityAxis.TRUST, "sort_order": 3},
    {"key": "quality_tier", "label": "Quality tier", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 4},
    {"key": "origin", "label": "Origin", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 5},
    {"key": "local_or_import", "label": "Local or import", "consumer_label": None, "data_type": AttributeDataType.ENUM, "unit": None, "quality_axis": None, "sort_order": 6},
    {"key": "zesa_survival", "label": "ZESA survival", "consumer_label": "Survives power cuts?", "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 7},
    {"key": "storage_life", "label": "Storage life", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 8},
    {"key": "seasonality", "label": "Seasonality", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 9},
    {"key": "where_to_buy", "label": "Where to buy", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 10},
    {"key": "price_source", "label": "Source price as published", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 11},
]


# ============================================================================
# 2. ALL 25 RETAIL PRODUCT CATEGORIES
# ============================================================================
RETAIL_CATEGORIES = [
    {"slug": "cooking-oil", "name": "Cooking oil", "synonyms": ["oil", "vegetable oil", "sunflower oil", "mafuta"]},
    {"slug": "maize-meal-roller-meal", "name": "Maize meal (roller meal)", "synonyms": ["mealie meal", "roller meal", "upfu", "corn meal", "refined meal"]},
    {"slug": "rice", "name": "Rice", "synonyms": ["mupunga"]},
    {"slug": "sugar", "name": "Sugar", "synonyms": ["shuga", "white sugar", "brown sugar"]},
    {"slug": "bread", "name": "Bread", "synonyms": ["loaf", "chingwa", "bakery"]},
    {"slug": "milk", "name": "Milk", "synonyms": ["mukaka", "fresh milk", "uht milk", "long life milk"]},
    {"slug": "chicken", "name": "Chicken", "synonyms": ["huku", "poultry", "broiler", "chicken pieces"]},
    {"slug": "eggs", "name": "Eggs", "synonyms": ["mazai", "tray of eggs"]},
    {"slug": "cement", "name": "Cement", "synonyms": ["builders cement", "portland cement", "bag of cement"]},
    {"slug": "solar-panel", "name": "Solar Panel", "synonyms": ["solar", "solar panel", "pv panel", "off-grid power"]},
    {"slug": "inverter", "name": "Inverter", "synonyms": ["inverter", "backup power", "battery backup", "ups"]},
    {"slug": "wheat-flour", "name": "Wheat flour", "synonyms": ["flour", "baking flour", "upfu hwe wheat"]},
    {"slug": "salt", "name": "Salt", "synonyms": ["munyu", "table salt"]},
    {"slug": "soya-chunks", "name": "Soya chunks", "synonyms": ["soya", "soya mince", "texture protein"]},
    {"slug": "groundnuts-peanuts", "name": "Groundnuts / Peanuts", "synonyms": ["nzungu", "peanuts", "groundnuts"]},
    {"slug": "toothbrushes", "name": "Toothbrushes", "synonyms": ["toothbrush", "oral care"]},
    {"slug": "ibr-roofing", "name": "IBR Roofing", "synonyms": ["roofing sheets", "zinc", "iron sheets", "ibr"]},
    {"slug": "maize-grain", "name": "Maize grain", "synonyms": ["chibage", "maize", "grain"]},
    {"slug": "pasta-spaghetti", "name": "Pasta / Spaghetti", "synonyms": ["pasta", "spaghetti", "macaroni"]},
    {"slug": "dried-beans-sugar-beans", "name": "Dried beans / Sugar beans", "synonyms": ["beans", "sugar beans", "nyemba"]},
    {"slug": "beef", "name": "Beef", "synonyms": ["nyama", "steak", "red meat", "butchery"]},
    {"slug": "tomatoes", "name": "Tomatoes", "synonyms": ["tomato", "madomasi"]},
    {"slug": "matches", "name": "Matches", "synonyms": ["matchbox", "matches", "njodzi"]},
    {"slug": "goat-meat-chevon", "name": "Goat Meat / Chevon", "synonyms": ["goat", "chevon", "mbudzi"]},
    {"slug": "beef-offal", "name": "Beef Offal", "synonyms": ["offal", "matumbu", "tripe", "liver"]},
]


# ============================================================================
# 3. RETAIL PROVIDERS / SUPERMARKETS / HARDWARE CHAINS
# ============================================================================
RETAIL_PROVIDERS = [
    {
        "name": "OK Zimbabwe",
        "website_url": "https://www.okzim.co.zw",
        "corporate_domain": "okzim.co.zw",
        "description": "Leading Zimbabwean retail and supermarket chain nationwide"
    },
    {
        "name": "TM Pick n Pay",
        "website_url": "https://www.tmpicknpay.co.zw",
        "corporate_domain": "tmpicknpay.co.zw",
        "description": "Major supermarket chain offering groceries and household essentials"
    },
    {
        "name": "Spar Zimbabwe",
        "website_url": "https://www.spar.co.zw",
        "corporate_domain": "spar.co.zw",
        "description": "Independent supermarket retail network across Zimbabwe"
    },
    {
        "name": "Choppies",
        "website_url": "https://www.choppies.co.zw",
        "corporate_domain": "choppies.co.zw",
        "description": "Value supermarket retail chain"
    },
    {
        "name": "Gain Cash & Carry",
        "website_url": "https://www.gain.co.zw",
        "corporate_domain": "gain.co.zw",
        "description": "Leading wholesale and bulk commodity distributor"
    },
    {
        "name": "Halsted Builders",
        "website_url": "https://www.halsted.co.zw",
        "corporate_domain": "halsted.co.zw",
        "description": "Hardware and building supplies retailer in Zimbabwe"
    },
    {
        "name": "PPC Zimbabwe",
        "website_url": "https://www.ppc.co.zw",
        "corporate_domain": "ppc.co.zw",
        "description": "Major portland cement manufacturer and distributor"
    },
    {
        "name": "Chloride Zimbabwe",
        "website_url": "https://www.chloride.co.zw",
        "corporate_domain": "chloride.co.zw",
        "description": "Automotive battery, solar battery, and inverter supplier"
    }
]


# ============================================================================
# 4. SAMPLE RETAIL PRODUCT LISTINGS
# ============================================================================
SAMPLE_RETAIL_LISTINGS = [
    # Cooking Oil
    {
        "provider": "OK Zimbabwe",
        "category_slug": "cooking-oil",
        "name": "Dendairy Sunflower Oil 2L",
        "price": 4.80,
        "source_url": "https://www.okzim.co.zw/groceries/oil",
        "description": "Pure refined sunflower cooking oil 2L bottle",
        "attributes": {
            "brand": "Dendairy",
            "pack_size": "2L",
            "unit_price_usd": 2.40,
            "counterfeit_risk_level": 1,
            "quality_tier": "standard",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "shelf-stable",
            "storage_life": "24 months",
            "seasonality": "year-round",
            "where_to_buy": "supermarkets",
            "price_source": "USD 4.80 / 2L"
        }
    },
    # Maize Meal
    {
        "provider": "TM Pick n Pay",
        "category_slug": "maize-meal-roller-meal",
        "name": "Ngwerewere Super Roller Meal 10kg",
        "price": 6.50,
        "source_url": "https://www.tmpicknpay.co.zw/groceries/mealie-meal",
        "description": "Top quality super refined roller meal 10kg bag",
        "attributes": {
            "brand": "Ngwerewere",
            "pack_size": "10kg",
            "unit_price_usd": 0.65,
            "counterfeit_risk_level": 1,
            "quality_tier": "standard",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "shelf-stable",
            "storage_life": "12 months",
            "seasonality": "year-round",
            "where_to_buy": "supermarkets, wholesale",
            "price_source": "USD 6.50 / 10kg"
        }
    },
    # Sugar
    {
        "provider": "Spar Zimbabwe",
        "category_slug": "sugar",
        "name": "Gold Star White Sugar 2kg",
        "price": 2.60,
        "source_url": "https://www.spar.co.zw/sugar",
        "description": "Fine granulated white cane sugar 2kg pack",
        "attributes": {
            "brand": "Gold Star",
            "pack_size": "2kg",
            "unit_price_usd": 1.30,
            "counterfeit_risk_level": 1,
            "quality_tier": "standard",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "shelf-stable",
            "storage_life": "36 months",
            "seasonality": "year-round",
            "where_to_buy": "supermarkets",
            "price_source": "USD 2.60 / 2kg"
        }
    },
    # Bread
    {
        "provider": "OK Zimbabwe",
        "category_slug": "bread",
        "name": "Bakers Inn White Loaf 700g",
        "price": 1.00,
        "source_url": "https://www.okzim.co.zw/bakery/bread",
        "description": "Freshly baked soft white sliced bread loaf",
        "attributes": {
            "brand": "Bakers Inn",
            "pack_size": "700g",
            "unit_price_usd": 1.43,
            "counterfeit_risk_level": 1,
            "quality_tier": "standard",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "1-3 days shelf life",
            "storage_life": "5 days",
            "seasonality": "year-round",
            "where_to_buy": "supermarkets, tuckshops",
            "price_source": "USD 1.00 / loaf"
        }
    },
    # Milk
    {
        "provider": "TM Pick n Pay",
        "category_slug": "milk",
        "name": "Dairibord Chimombe Full Cream Milk 1L",
        "price": 1.40,
        "source_url": "https://www.tmpicknpay.co.zw/dairy/milk",
        "description": "UHT long life full cream cow milk 1L carton",
        "attributes": {
            "brand": "Dairibord",
            "pack_size": "1L",
            "unit_price_usd": 1.40,
            "counterfeit_risk_level": 1,
            "quality_tier": "standard",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "unopened shelf-stable",
            "storage_life": "6 months",
            "seasonality": "year-round",
            "where_to_buy": "supermarkets",
            "price_source": "USD 1.40 / 1L"
        }
    },
    # Chicken
    {
        "provider": "Gain Cash & Carry",
        "category_slug": "chicken",
        "name": "Irvines Fresh Frozen Mixed Chicken Portions 2kg",
        "price": 5.50,
        "source_url": "https://www.gain.co.zw/frozen/chicken",
        "description": "Frozen mixed chicken portions with brine injection 2kg pack",
        "attributes": {
            "brand": "Irvines",
            "pack_size": "2kg",
            "unit_price_usd": 2.75,
            "counterfeit_risk_level": 1,
            "quality_tier": "standard",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "requires cold storage / backup power",
            "storage_life": "9 months frozen",
            "seasonality": "year-round",
            "where_to_buy": "butcheries, supermarkets",
            "price_source": "USD 5.50 / 2kg"
        }
    },
    # Eggs
    {
        "provider": "Spar Zimbabwe",
        "category_slug": "eggs",
        "name": "Crest Poultry Fresh Table Eggs Tray of 30",
        "price": 4.20,
        "source_url": "https://www.spar.co.zw/eggs",
        "description": "Large fresh farm table eggs tray of 30",
        "attributes": {
            "brand": "Crest Poultry",
            "pack_size": "tray of 30",
            "unit_price_usd": 0.14,
            "counterfeit_risk_level": 1,
            "quality_tier": "standard",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "shelf-stable 3 weeks",
            "storage_life": "3 weeks",
            "seasonality": "year-round",
            "where_to_buy": "supermarkets, open markets",
            "price_source": "USD 4.20 / 30 eggs"
        }
    },
    # Cement
    {
        "provider": "Halsted Builders",
        "category_slug": "cement",
        "name": "PPC Surebuild 42.5N Portland Cement 50kg",
        "price": 10.50,
        "source_url": "https://www.halsted.co.zw/building/cement",
        "description": "High strength premium portland building cement 50kg bag",
        "attributes": {
            "brand": "PPC",
            "pack_size": "50kg",
            "unit_price_usd": 0.21,
            "counterfeit_risk_level": 2,
            "quality_tier": "premium",
            "origin": "Zimbabwe",
            "local_or_import": "local",
            "zesa_survival": "weather-proof dry storage",
            "storage_life": "6 months dry",
            "seasonality": "year-round",
            "where_to_buy": "hardware stores, building suppliers",
            "price_source": "USD 10.50 / 50kg"
        }
    },
    # Solar Panel
    {
        "provider": "Chloride Zimbabwe",
        "category_slug": "solar-panel",
        "name": "Canadian Solar 550W Mono PERC Solar Panel",
        "price": 95.00,
        "source_url": "https://www.chloride.co.zw/solar/panels",
        "description": "High efficiency monocrystalline half-cell photovoltaic panel 550W",
        "attributes": {
            "brand": "Canadian Solar",
            "pack_size": "550W",
            "unit_price_usd": 0.17,
            "counterfeit_risk_level": 2,
            "quality_tier": "tier 1",
            "origin": "China",
            "local_or_import": "import",
            "zesa_survival": "off-grid generation",
            "storage_life": "25 years warranty",
            "seasonality": "year-round",
            "where_to_buy": "solar and electrical suppliers",
            "price_source": "USD 95.00 / 550W"
        }
    },
    # Inverter
    {
        "provider": "Chloride Zimbabwe",
        "category_slug": "inverter",
        "name": "Must 5kW 48V Hybrid Solar Inverter",
        "price": 450.00,
        "source_url": "https://www.chloride.co.zw/solar/inverters",
        "description": "Pure sine wave hybrid inverter with 80A MPPT solar charge controller",
        "attributes": {
            "brand": "Must",
            "pack_size": "5000W",
            "unit_price_usd": 0.09,
            "counterfeit_risk_level": 2,
            "quality_tier": "standard",
            "origin": "China",
            "local_or_import": "import",
            "zesa_survival": "seamless backup power",
            "storage_life": "5 years life",
            "seasonality": "year-round",
            "where_to_buy": "solar distributors",
            "price_source": "USD 450.00 / unit"
        }
    }
]


def seed_retail_sector(db=None):
    """Seed Retail sector, all 25 categories, 12 schema fields, providers, and listings."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        print("[Retail Seed] Starting Retail & Groceries Sector database seed...")

        # 1. Ensure Retail sector exists and is LIVE
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "retail").first()
        if not sector:
            sector = SectorConfig(
                id=_uid(),
                name="Retail & Groceries",
                slug="retail",
                status=SectorStatus.LIVE,
                icon="shopping-cart",
                blurb="Compare commodity prices, grocery essentials, hardware, building materials and solar energy equipment"
            )
            db.add(sector)
            db.flush()
            print("  [+] Created Sector: Retail & Groceries")
        else:
            sector.name = "Retail & Groceries"
            sector.status = SectorStatus.LIVE
            db.flush()

        # 2. Seed All 25 Categories & Attribute Schemas
        cat_map = {}
        for cat_spec in RETAIL_CATEGORIES:
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

            # Upsert all 12 schema fields for this category
            for f in COMMON_RETAIL_FIELDS:
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
                        quality_axis=f.get("quality_axis"),
                        is_comparable=True
                    )
                    db.add(attr)
                else:
                    attr.label = f["label"]
                    attr.consumer_label = f.get("consumer_label")
                    attr.data_type = f["data_type"]
                    attr.unit = f.get("unit")
                    attr.sort_order = f.get("sort_order", 0)
                    attr.quality_axis = f.get("quality_axis")
                    attr.is_comparable = True

        # 3. Seed Retail Providers
        provider_map = {}
        for p_data in RETAIL_PROVIDERS:
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
                print(f"  [+] Retail Provider: {provider.name}")
            else:
                provider.website_url = p_data.get("website_url")
                provider.corporate_domain = p_data.get("corporate_domain")
                provider.description = p_data.get("description")
                db.flush()
            provider_map[p_data["name"]] = provider

        # 4. Seed Retail Product Listings
        now = datetime.utcnow()
        for item in SAMPLE_RETAIL_LISTINGS:
            cat = cat_map.get(item["category_slug"])
            provider = provider_map.get(item["provider"])
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
        print(f"[Retail Seed] Successfully seeded {len(RETAIL_CATEGORIES)} categories with 12-field schemas, providers, and listings!")
    except Exception as e:
        db.rollback()
        print(f"[Retail Seed] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_retail_sector()
