"""
Food & Drink Sector Database Seed
Implements:
1. Sector: food ("Food & Drink")
2. Categories: fast-food, casual-dining
3. Attribute schema fields:
   - fast-food: meal (string), delivery (boolean, availability), halal (boolean)
   - casual-dining: cuisine (string), seating (boolean, availability)
4. Restaurant chains (Providers) & sample menu listings
"""
import uuid
from typing import Dict, Any, List
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
# 1. FOOD CATEGORIES & ATTRIBUTE SCHEMAS
# ============================================================================
FOOD_CATEGORIES = [
    {
        "slug": "fast-food",
        "name": "Fast food",
        "synonyms": ["takeaway", "quick meal", "fast food chains", "burgers", "fried chicken", "pizza"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "meal", "label": "Meal", "consumer_label": "Menu item name", "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 0},
            {"key": "delivery", "label": "Delivery available", "consumer_label": "Home / Office delivery", "data_type": AttributeDataType.BOOLEAN, "unit": None, "quality_axis": QualityAxis.AVAILABILITY, "sort_order": 1},
            {"key": "halal", "label": "Halal", "consumer_label": "Halal certified", "data_type": AttributeDataType.BOOLEAN, "unit": None, "quality_axis": None, "sort_order": 2},
        ]
    },
    {
        "slug": "casual-dining",
        "name": "Casual dining",
        "synonyms": ["restaurant", "sit-down meal", "dining", "bistro", "cafe"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "cuisine", "label": "Cuisine", "consumer_label": "Cuisine style (e.g. Italian, Fusion, Zimbabwean)", "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 0},
            {"key": "seating", "label": "Seating available", "consumer_label": "Dine-in seating", "data_type": AttributeDataType.BOOLEAN, "unit": None, "quality_axis": QualityAxis.AVAILABILITY, "sort_order": 1},
        ]
    }
]


# ============================================================================
# 2. RESTAURANT CHAINS & OUTLETS (PROVIDERS)
# ============================================================================
FOOD_PROVIDERS = [
    # Fast Food Chains
    {
        "name": "Chicken Inn",
        "category": "fast-food",
        "website_url": "https://www.simbisa.co.zw/chicken-inn",
        "corporate_domain": "chickeninn.co.zw",
        "description": "Leading Zimbabwean quick service fried chicken brand"
    },
    {
        "name": "Pizza Inn",
        "category": "fast-food",
        "website_url": "https://www.simbisa.co.zw/pizza-inn",
        "corporate_domain": "pizzainn.co.zw",
        "description": "Pan and classic pizza quick service chain"
    },
    {
        "name": "Nando's",
        "category": "fast-food",
        "website_url": "https://www.nandos.co.zw",
        "corporate_domain": "nandos.co.zw",
        "description": "Flame-grilled peri-peri chicken restaurant chain"
    },
    {
        "name": "Steers",
        "category": "fast-food",
        "website_url": "https://www.steers.co.zw",
        "corporate_domain": "steers.co.zw",
        "description": "Flame-grilled burgers and chips fast food outlet"
    },
    {
        "name": "RocoMamas",
        "category": "fast-food",
        "website_url": "https://www.rocomamas.co.zw",
        "corporate_domain": "rocomamas.co.zw",
        "description": "Smashburgers, ribs, and wings fast casual diner"
    },

    # Casual Dining Restaurants
    {
        "name": "Victoria 22",
        "category": "casual-dining",
        "website_url": "https://www.victoria22.co.zw",
        "corporate_domain": "victoria22.co.zw",
        "description": "Fine and casual Mediterranean & European dining in Newlands, Harare"
    },
    {
        "name": "Cafe Nush",
        "category": "casual-dining",
        "website_url": "https://www.cafenush.co.zw",
        "corporate_domain": "cafenush.co.zw",
        "description": "Contemporary cafe, bakery, and bistro dining across Harare"
    },
    {
        "name": "Moyo Restaurant",
        "category": "casual-dining",
        "website_url": "https://www.moyo.co.zw",
        "corporate_domain": "moyo.co.zw",
        "description": "Authentic African cuisine and traditional dining experience"
    },
    {
        "name": "Amanzi Restaurant",
        "category": "casual-dining",
        "website_url": "https://www.amanzi.co.zw",
        "corporate_domain": "amanzi.co.zw",
        "description": "International contemporary restaurant in lush garden setting in Highlands, Harare"
    }
]


# ============================================================================
# 3. SAMPLE MENU LISTINGS
# ============================================================================
SAMPLE_FOOD_LISTINGS = [
    # Fast Food
    {
        "restaurant": "Chicken Inn",
        "category_slug": "fast-food",
        "name": "Chicken Inn — 2-Piece Chicken Combo",
        "price": 3.00,
        "source_url": "https://www.chickeninn.co.zw/menu",
        "description": "2 pieces of golden fried chicken served with regular chips and a 330ml soda",
        "attributes": {
            "meal": "2-Piece Chicken Combo",
            "delivery": True,
            "halal": False
        }
    },
    {
        "restaurant": "Chicken Inn",
        "category_slug": "fast-food",
        "name": "Chicken Inn — Family Barrel (8 Pieces)",
        "price": 12.00,
        "source_url": "https://www.chickeninn.co.zw/menu",
        "description": "8 pieces of seasoned fried chicken with 2 large portions of chips",
        "attributes": {
            "meal": "Family Barrel (8 Pieces)",
            "delivery": True,
            "halal": False
        }
    },
    {
        "restaurant": "Pizza Inn",
        "category_slug": "fast-food",
        "name": "Pizza Inn — Large BBQ Chicken Pizza",
        "price": 9.50,
        "source_url": "https://www.pizzainn.co.zw/menu",
        "description": "Large 30cm pizza with chicken strips, BBQ sauce, mozzarella and mushrooms",
        "attributes": {
            "meal": "Large BBQ Chicken Pizza",
            "delivery": True,
            "halal": False
        }
    },
    {
        "restaurant": "Pizza Inn",
        "category_slug": "fast-food",
        "name": "Pizza Inn — Medium Veg Feast Pizza",
        "price": 6.50,
        "source_url": "https://www.pizzainn.co.zw/menu",
        "description": "Medium 23cm vegetarian pizza with peppers, olives, mushrooms, sweetcorn",
        "attributes": {
            "meal": "Medium Veg Feast Pizza",
            "delivery": True,
            "halal": True
        }
    },
    {
        "restaurant": "Nando's",
        "category_slug": "fast-food",
        "name": "Nando's — 1/4 Chicken & Single Side",
        "price": 5.00,
        "source_url": "https://www.nandos.co.zw/menu",
        "description": "Flame-grilled 1/4 peri-peri chicken served with spicy rice or peri-chips",
        "attributes": {
            "meal": "1/4 Chicken & Single Side",
            "delivery": True,
            "halal": True
        }
    },
    {
        "restaurant": "Nando's",
        "category_slug": "fast-food",
        "name": "Nando's — Full Platter",
        "price": 18.50,
        "source_url": "https://www.nandos.co.zw/menu",
        "description": "Whole flame-grilled chicken with 2 large sharing sides",
        "attributes": {
            "meal": "Full Platter",
            "delivery": True,
            "halal": True
        }
    },

    # Casual Dining
    {
        "restaurant": "Victoria 22",
        "category_slug": "casual-dining",
        "name": "Victoria 22 — Grilled Kariba Bream Fillet",
        "price": 16.50,
        "source_url": "https://www.victoria22.co.zw/menu",
        "description": "Pan-seared fresh Kariba bream with lemon butter sauce and seasonal greens",
        "attributes": {
            "cuisine": "Mediterranean & Seafood",
            "seating": True
        }
    },
    {
        "restaurant": "Victoria 22",
        "category_slug": "casual-dining",
        "name": "Victoria 22 — Beef Fillet Mignon",
        "price": 21.00,
        "source_url": "https://www.victoria22.co.zw/menu",
        "description": "Tender beef tenderloin with pepper crust and red wine reduction",
        "attributes": {
            "cuisine": "Continental",
            "seating": True
        }
    },
    {
        "restaurant": "Cafe Nush",
        "category_slug": "casual-dining",
        "name": "Cafe Nush — Gourmet Chicken Burger",
        "price": 8.50,
        "source_url": "https://www.cafenush.co.zw/menu",
        "description": "Grilled breast fillet, smashed avocado, bacon and house fries",
        "attributes": {
            "cuisine": "Bistro / Cafe",
            "seating": True
        }
    },
    {
        "restaurant": "Cafe Nush",
        "category_slug": "casual-dining",
        "name": "Cafe Nush — Wood-fired Margherita Pizza",
        "price": 10.00,
        "source_url": "https://www.cafenush.co.zw/menu",
        "description": "Artisan sourdough base with San Marzano tomato sauce and fresh basil",
        "attributes": {
            "cuisine": "Italian",
            "seating": True
        }
    },
    {
        "restaurant": "Moyo Restaurant",
        "category_slug": "casual-dining",
        "name": "Moyo Restaurant — Traditional Roadrunner Chicken",
        "price": 14.00,
        "source_url": "https://www.moyo.co.zw/menu",
        "description": "Slow-cooked organic free-range chicken with sadza and covo",
        "attributes": {
            "cuisine": "Zimbabwean",
            "seating": True
        }
    }
]


def seed_food_sector(db=None):
    """Seed Food & Drink sector, categories, attribute schemas, restaurant providers, and menu listings."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        print("[Food Seed] Starting Food & Drink Sector database seed...")

        # 1. Ensure Food sector exists and is LIVE
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "food").first()
        if not sector:
            sector = SectorConfig(
                id=_uid(),
                name="Food & Drink",
                slug="food",
                status=SectorStatus.LIVE,
                icon="utensils",
                blurb="Compare restaurant menus, fast food combos, casual dining prices and delivery options"
            )
            db.add(sector)
            db.flush()
            print("  [+] Created Sector: Food & Drink")
        else:
            sector.name = "Food & Drink"
            sector.status = SectorStatus.LIVE
            db.flush()

        # 2. Seed 2 Categories & Attribute Schemas
        cat_map = {}
        for cat_spec in FOOD_CATEGORIES:
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

            # Upsert schema fields
            for f in cat_spec.get("fields", []):
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
                        data_type=f.get("data_type", AttributeDataType.STRING),
                        unit=f.get("unit"),
                        sort_order=f.get("sort_order", 0),
                        quality_axis=f.get("quality_axis"),
                        is_comparable=True
                    )
                    db.add(attr)
                else:
                    attr.label = f["label"]
                    attr.consumer_label = f.get("consumer_label")
                    attr.data_type = f.get("data_type", AttributeDataType.STRING)
                    attr.unit = f.get("unit")
                    attr.sort_order = f.get("sort_order", 0)
                    attr.quality_axis = f.get("quality_axis")
                    attr.is_comparable = True

        # 3. Seed Restaurant Providers
        provider_map = {}
        for p_data in FOOD_PROVIDERS:
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
                print(f"  [+] Restaurant Provider: {provider.name}")
            else:
                provider.website_url = p_data.get("website_url")
                provider.corporate_domain = p_data.get("corporate_domain")
                provider.description = p_data.get("description")
                db.flush()
            provider_map[p_data["name"]] = provider

        # 4. Seed Food Menu Listings
        now = datetime.utcnow()
        for item in SAMPLE_FOOD_LISTINGS:
            cat = cat_map.get(item["category_slug"])
            provider = provider_map.get(item["restaurant"])
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
        print("[Food Seed] Successfully seeded Food & Drink sector, categories, restaurant providers, and menu listings!")
    except Exception as e:
        db.rollback()
        print(f"[Food Seed] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_food_sector()
