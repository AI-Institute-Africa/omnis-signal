"""
Hotels Sector Database Seed
Implements:
1. Sector: hotels ("Hotels", status = live)
2. Category: hotel-stays ("Hotels & stays")
3. Attribute schema fields:
   - price_per_night (number, USD)
   - room_type (enum)
   - location (string)
   - breakfast_included (boolean)
   - pool (boolean)
4. Seeded hotel providers: Meikles, Rainbow Towers, Cresta, Holiday Inn, Victoria Falls Safari Lodge, Kingdom Hotel
5. Sample room rate listings
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
# 1. HOTELS CATEGORY & ATTRIBUTE SCHEMA
# ============================================================================
HOTELS_CATEGORIES = [
    {
        "slug": "hotel-stays",
        "name": "Hotels & stays",
        "synonyms": [],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "price_per_night", "label": "Price per night", "consumer_label": "Nightly room rate", "data_type": AttributeDataType.NUMBER, "unit": "USD", "quality_axis": None, "sort_order": 0},
            {"key": "room_type", "label": "Room type", "consumer_label": "standard, deluxe, executive, suite, family, studio, villa", "data_type": AttributeDataType.ENUM, "unit": None, "quality_axis": None, "sort_order": 1},
            {"key": "location", "label": "Location", "consumer_label": "City / Destination", "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 2},
            {"key": "breakfast_included", "label": "Breakfast included", "consumer_label": "Complimentary breakfast", "data_type": AttributeDataType.BOOLEAN, "unit": None, "quality_axis": None, "sort_order": 3},
            {"key": "pool", "label": "Swimming pool", "consumer_label": "On-site swimming pool", "data_type": AttributeDataType.BOOLEAN, "unit": None, "quality_axis": None, "sort_order": 4},
        ]
    }
]


# ============================================================================
# 2. HOTEL PROVIDERS
# ============================================================================
HOTEL_PROVIDERS = [
    {
        "name": "Meikles",
        "website_url": "https://www.meikles.com",
        "corporate_domain": "meikles.com",
        "description": "Historic 5-star luxury hotel in central Harare overlooking Africa Unity Square"
    },
    {
        "name": "Rainbow Towers",
        "website_url": "https://www.rtgafrica.com/rainbow-towers-hotel",
        "corporate_domain": "rtgafrica.com",
        "description": "Flagship 5-star conference and leisure hotel and international convention centre in Harare"
    },
    {
        "name": "Cresta",
        "website_url": "https://www.crestahotels.com",
        "corporate_domain": "crestahotels.com",
        "description": "Leading Southern African hospitality group with multiple hotels across Harare and Victoria Falls"
    },
    {
        "name": "Holiday Inn",
        "website_url": "https://www.ihg.com/holidayinn/harare",
        "corporate_domain": "holidayinnharare.co.zw",
        "description": "Full-service contemporary business hotel in Harare and Bulawayo"
    },
    {
        "name": "Victoria Falls Safari Lodge",
        "website_url": "https://www.victoria-falls-safari-lodge.com",
        "corporate_domain": "africaalbidatourism.com",
        "description": "Iconic safari lodge situated on a plateau overlooking the Zambezi National Park waterhole"
    },
    {
        "name": "Kingdom Hotel",
        "website_url": "https://www.thekingdomhotel.co.zw",
        "corporate_domain": "thekingdomhotel.co.zw",
        "description": "Resort style hotel with Great Zimbabwe architecture in Victoria Falls"
    }
]


# ============================================================================
# 3. SAMPLE ROOM RATE LISTINGS
# ============================================================================
SAMPLE_HOTEL_LISTINGS = [
    {
        "hotel": "Cresta",
        "name": "Cresta Standard Room",
        "price": 85.00,
        "source_url": "https://www.crestahotels.com/harare/rates",
        "description": "Standard room, $85 per night, breakfast included, pool on site",
        "attributes": {
            "price_per_night": 85.00,
            "room_type": "standard",
            "location": "Harare",
            "breakfast_included": True,
            "pool": True
        }
    },
    {
        "hotel": "Cresta",
        "name": "Cresta — Deluxe Executive Room",
        "price": 135.00,
        "source_url": "https://www.crestahotels.com/harare/rates",
        "description": "Spacious executive room with city view, king bed and work desk",
        "attributes": {
            "price_per_night": 135.00,
            "room_type": "executive",
            "location": "Harare",
            "breakfast_included": True,
            "pool": True
        }
    },
    {
        "hotel": "Meikles",
        "name": "Meikles — Deluxe Room",
        "price": 175.00,
        "source_url": "https://www.meikles.com/accommodation",
        "description": "Luxury deluxe room in the North Wing with marble bathroom and park views",
        "attributes": {
            "price_per_night": 175.00,
            "room_type": "deluxe",
            "location": "Harare",
            "breakfast_included": True,
            "pool": True
        }
    },
    {
        "hotel": "Meikles",
        "name": "Meikles — Presidential Suite",
        "price": 450.00,
        "source_url": "https://www.meikles.com/accommodation",
        "description": "Ultra-luxury presidential suite with private dining, lounge and butler service",
        "attributes": {
            "price_per_night": 450.00,
            "room_type": "suite",
            "location": "Harare",
            "breakfast_included": True,
            "pool": True
        }
    },
    {
        "hotel": "Rainbow Towers",
        "name": "Rainbow Towers — Standard King Room",
        "price": 120.00,
        "source_url": "https://www.rtgafrica.com/rainbow-towers-hotel/rates",
        "description": "Comfortable king-bed room with panoramic city views and high-speed WiFi",
        "attributes": {
            "price_per_night": 120.00,
            "room_type": "standard",
            "location": "Harare",
            "breakfast_included": False,
            "pool": True
        }
    },
    {
        "hotel": "Holiday Inn",
        "name": "Holiday Inn — Superior Twin Room",
        "price": 110.00,
        "source_url": "https://www.ihg.com/holidayinn/harare/rates",
        "description": "Contemporary twin room with ergonomic workspace and coffee facilities",
        "attributes": {
            "price_per_night": 110.00,
            "room_type": "twin",
            "location": "Harare",
            "breakfast_included": True,
            "pool": True
        }
    },
    {
        "hotel": "Victoria Falls Safari Lodge",
        "name": "Victoria Falls Safari Lodge — Safari Club Suite",
        "price": 320.00,
        "source_url": "https://www.victoria-falls-safari-lodge.com/rates",
        "description": "Uninterrupted sunset views over the waterhole with private balcony",
        "attributes": {
            "price_per_night": 320.00,
            "room_type": "suite",
            "location": "Victoria Falls",
            "breakfast_included": True,
            "pool": True
        }
    },
    {
        "hotel": "Kingdom Hotel",
        "name": "Kingdom Hotel — Family Room",
        "price": 190.00,
        "source_url": "https://www.thekingdomhotel.co.zw/rates",
        "description": "Family room accommodating 2 adults and 2 children, close to Victoria Falls rainforest",
        "attributes": {
            "price_per_night": 190.00,
            "room_type": "family",
            "location": "Victoria Falls",
            "breakfast_included": True,
            "pool": True
        }
    }
]


def seed_hotels_sector(db=None):
    """Seed Hotels sector, hotel-stays category, attribute schema, hotel providers, and room listings."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        print("[Hotels Seed] Starting Hotels Sector database seed...")

        # 1. Ensure Hotels sector exists and is LIVE
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "hotels").first()
        if not sector:
            sector = SectorConfig(
                id=_uid(),
                name="Hotels",
                slug="hotels",
                status=SectorStatus.LIVE,
                icon="hotel",
                blurb="Compare hotel rates, safari lodges, room packages, breakfast inclusion and amenities"
            )
            db.add(sector)
            db.flush()
            print("  [+] Created Sector: Hotels")
        else:
            sector.name = "Hotels"
            sector.status = SectorStatus.LIVE
            db.flush()

        # 2. Seed hotel-stays Category & Attribute Schema
        cat_spec = HOTELS_CATEGORIES[0]
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
                    quality_axis=None,
                    is_comparable=True
                )
                db.add(attr)
            else:
                attr.label = f["label"]
                attr.consumer_label = f.get("consumer_label")
                attr.data_type = f.get("data_type", AttributeDataType.STRING)
                attr.unit = f.get("unit")
                attr.sort_order = f.get("sort_order", 0)
                attr.quality_axis = None
                attr.is_comparable = True

        # 3. Seed Hotel Providers
        provider_map = {}
        for p_data in HOTEL_PROVIDERS:
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
                print(f"  [+] Hotel Provider: {provider.name}")
            else:
                provider.website_url = p_data.get("website_url")
                provider.corporate_domain = p_data.get("corporate_domain")
                provider.description = p_data.get("description")
                db.flush()
            provider_map[p_data["name"]] = provider

        # 4. Seed Hotel Room Listings
        now = datetime.utcnow()
        for item in SAMPLE_HOTEL_LISTINGS:
            provider = provider_map.get(item["hotel"])
            if not provider:
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
        print("[Hotels Seed] Successfully seeded Hotels sector, category, providers, and room rate listings!")
    except Exception as e:
        db.rollback()
        print(f"[Hotels Seed] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_hotels_sector()
