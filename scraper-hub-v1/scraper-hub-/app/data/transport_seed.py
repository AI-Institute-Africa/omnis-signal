"""
Transport Sector Database Seed
Implements:
1. Sector: transport ("Transport", status = live)
2. 8 Transport Categories sharing the common 16-field attribute schema
3. Transport Providers / Operators (ZUPCO, Bolt, inDrive, Vaya, Fastjet, etc.)
4. Sample transport service and fare listings
"""
import uuid
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
# 1. COMMON 16-FIELD ATTRIBUTE SCHEMA SPECIFICATION
# ============================================================================
COMMON_TRANSPORT_FIELDS = [
    {"key": "service_level", "label": "Service level", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 0},
    {"key": "fare_gazetted", "label": "Gazetted fare", "consumer_label": "Official (gazetted) fare", "data_type": AttributeDataType.NUMBER, "unit": "USD", "quality_axis": None, "sort_order": 1},
    {"key": "fare_estimate", "label": "Real fare with levies", "consumer_label": "What you actually pay", "data_type": AttributeDataType.NUMBER, "unit": "USD", "quality_axis": None, "sort_order": 2},
    {"key": "punctuality_score", "label": "Punctuality", "consumer_label": "Punctuality (1-5)", "data_type": AttributeDataType.NUMBER, "unit": None, "quality_axis": QualityAxis.PERFORMANCE, "sort_order": 3},
    {"key": "comfort_score", "label": "Comfort", "consumer_label": "Comfort (1-5)", "data_type": AttributeDataType.NUMBER, "unit": None, "quality_axis": QualityAxis.PERFORMANCE, "sort_order": 4},
    {"key": "safety_score", "label": "Safety", "consumer_label": "Safety (1-5)", "data_type": AttributeDataType.NUMBER, "unit": None, "quality_axis": QualityAxis.TRUST, "sort_order": 5},
    {"key": "coverage_score", "label": "Coverage", "consumer_label": "Route coverage (1-5)", "data_type": AttributeDataType.NUMBER, "unit": None, "quality_axis": QualityAxis.AVAILABILITY, "sort_order": 6},
    {"key": "reliability_score", "label": "Reliability", "consumer_label": "Reliability (1-5)", "data_type": AttributeDataType.NUMBER, "unit": None, "quality_axis": QualityAxis.RESILIENCE, "sort_order": 7},
    {"key": "fleet_type", "label": "Fleet", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 8},
    {"key": "province_district", "label": "Province / district", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "quality_axis": None, "sort_order": 9},
    {"key": "ownership_status", "label": "Ownership", "consumer_label": None, "data_type": AttributeDataType.ENUM, "unit": None, "quality_axis": None, "sort_order": 10},
    {"key": "urbanicity", "label": "Urban or rural", "consumer_label": None, "data_type": AttributeDataType.ENUM, "unit": None, "quality_axis": None, "sort_order": 11},
    {"key": "passenger_or_freight", "label": "Passenger or freight", "consumer_label": None, "data_type": AttributeDataType.ENUM, "unit": None, "quality_axis": None, "sort_order": 12},
    {"key": "fuel_cost_per_trip", "label": "Fuel cost per trip", "consumer_label": None, "data_type": AttributeDataType.NUMBER, "unit": "USD", "quality_axis": None, "sort_order": 13},
    {"key": "toll_fee_per_trip", "label": "Toll per trip", "consumer_label": None, "data_type": AttributeDataType.NUMBER, "unit": "USD", "quality_axis": None, "sort_order": 14},
    {"key": "annual_cost_passenger", "label": "Annual cost to passenger", "consumer_label": None, "data_type": AttributeDataType.NUMBER, "unit": "USD", "quality_axis": None, "sort_order": 15},
]


# ============================================================================
# 2. ALL 8 TRANSPORT CATEGORIES
# ============================================================================
TRANSPORT_CATEGORIES = [
    {"slug": "urban-commuter", "name": "Urban Commuter", "synonyms": ["kombi", "commuter omnibus", "zupco", "city transport", "mushikashika"]},
    {"slug": "intercity", "name": "Intercity", "synonyms": ["long distance bus", "intercity bus", "coach", "bus to bulawayo"]},
    {"slug": "freight-cargo", "name": "Freight/Cargo", "synonyms": ["haulage", "truck", "cargo", "freight", "logistics"]},
    {"slug": "cross-border", "name": "Cross-Border", "synonyms": ["cross border bus", "bus to south africa", "johannesburg bus", "malawi bus"]},
    {"slug": "rural", "name": "Rural", "synonyms": ["rural transport", "village bus", "growth point"]},
    {"slug": "air", "name": "Air", "synonyms": ["flight", "plane", "airline", "domestic flight", "fastjet"]},
    {"slug": "last-mile", "name": "Last Mile", "synonyms": ["taxi", "bolt", "indrive", "ride hailing", "pirate taxi"]},
    {"slug": "contract-staff", "name": "Contract / Staff", "synonyms": ["staff transport", "company bus", "contract transport"]},
]


# ============================================================================
# 3. TRANSPORT OPERATORS (PROVIDERS)
# ============================================================================
TRANSPORT_PROVIDERS = [
    {
        "name": "ZUPCO - Urban",
        "website_url": "https://www.zupco.co.zw",
        "corporate_domain": "zupco.co.zw",
        "description": "Zimbabwe United Passenger Company urban commuter mass transit and franchised kombis"
    },
    {
        "name": "Bolt Zimbabwe",
        "website_url": "https://bolt.eu/en-zw",
        "corporate_domain": "bolt.eu",
        "description": "App-based on-demand ride hailing and last mile mobility service in Harare"
    },
    {
        "name": "inDrive",
        "website_url": "https://indrive.com",
        "corporate_domain": "indrive.com",
        "description": "Peer-to-peer fare negotiation ride hailing platform in Zimbabwe"
    },
    {
        "name": "Vaya Africa",
        "website_url": "https://www.vayaafrica.com",
        "corporate_domain": "vayaafrica.com",
        "description": "Digital logistics and ride hailing platform across Zimbabwean cities"
    },
    {
        "name": "Tshova Mubaiwa",
        "website_url": "https://www.tshovamubaiwa.co.zw",
        "corporate_domain": "tshovamubaiwa.co.zw",
        "description": "Bulawayo urban transport association and commuter omnibus operator"
    },
    {
        "name": "Extracity Luxury Coaches",
        "website_url": "https://www.extracity.co.zw",
        "corporate_domain": "extracity.co.zw",
        "description": "Intercity luxury passenger coach operator connecting Harare, Bulawayo, and Victoria Falls"
    },
    {
        "name": "Fastjet",
        "website_url": "https://www.fastjet.com",
        "corporate_domain": "fastjet.com",
        "description": "Award-winning value regional airline flying domestic routes in Zimbabwe"
    },
    {
        "name": "Intercape Zimbabwe",
        "website_url": "https://www.intercape.co.za",
        "corporate_domain": "intercape.co.za",
        "description": "Cross-border luxury sleeper coach service between Zimbabwe and South Africa"
    },
    {
        "name": "ZUPCO - Staff Bus Contract",
        "website_url": "https://www.zupco.co.zw/charter",
        "corporate_domain": "charter.zupco.co.zw",
        "description": "Dedicated contract transport for schools, universities, and industrial mines"
    }
]


# ============================================================================
# 4. SAMPLE TRANSPORT SERVICE LISTINGS
# ============================================================================
SAMPLE_TRANSPORT_LISTINGS = [
    # Urban Commuter - ZUPCO
    {
        "provider": "ZUPCO - Urban",
        "category_slug": "urban-commuter",
        "name": "ZUPCO Urban Commuter (Harare)",
        "fare_gazetted": 1.50,
        "fare_estimate": 1.50,
        "source_url": "https://www.zupco.co.zw/fares",
        "description": "Official gazetted city commuter omnibus route in Harare CBD",
        "attributes": {
            "service_level": "Standard",
            "fare_gazetted": 1.50,
            "fare_estimate": 1.50,
            "fleet_type": "Kombi",
            "province_district": "Harare CBD",
            "ownership_status": "state",
            "urbanicity": "urban",
            "passenger_or_freight": "passenger"
        }
    },
    # Last Mile - Bolt
    {
        "provider": "Bolt Zimbabwe",
        "category_slug": "last-mile",
        "name": "Bolt Economy Ride (Harare)",
        "fare_gazetted": None,
        "fare_estimate": 3.00,
        "source_url": "https://bolt.eu/en-zw/cities/harare",
        "description": "On-demand sedan ride across Harare metro area",
        "attributes": {
            "service_level": "Economy",
            "fare_gazetted": None,
            "fare_estimate": 3.00,
            "fleet_type": "Sedan",
            "province_district": "Harare Metro",
            "ownership_status": "private",
            "urbanicity": "urban",
            "passenger_or_freight": "passenger"
        }
    },
    # Intercity - Extracity
    {
        "provider": "Extracity Luxury Coaches",
        "category_slug": "intercity",
        "name": "Extracity Luxury Coach — Harare to Bulawayo",
        "fare_gazetted": 15.00,
        "fare_estimate": 15.00,
        "source_url": "https://www.extracity.co.zw/routes",
        "description": "Direct luxury AC coach service with reclining seats and onboard USB charging",
        "attributes": {
            "service_level": "Luxury",
            "fare_gazetted": 15.00,
            "fare_estimate": 15.00,
            "fleet_type": "Coach",
            "province_district": "Harare — Bulawayo",
            "ownership_status": "private",
            "urbanicity": "both",
            "passenger_or_freight": "passenger",
            "toll_fee_per_trip": 10.00
        }
    },
    # Air - Fastjet
    {
        "provider": "Fastjet",
        "category_slug": "air",
        "name": "Fastjet Domestic Flight — Harare to Victoria Falls",
        "fare_gazetted": 95.00,
        "fare_estimate": 115.00,
        "source_url": "https://www.fastjet.com/book",
        "description": "Scheduled domestic flight service operating daily between HRE and VFA",
        "attributes": {
            "service_level": "Standard FlyEarly",
            "fare_gazetted": 95.00,
            "fare_estimate": 115.00,
            "fleet_type": "Aircraft",
            "province_district": "Harare — Victoria Falls",
            "ownership_status": "private",
            "urbanicity": "urban",
            "passenger_or_freight": "passenger"
        }
    },
    # Cross-Border - Intercape
    {
        "provider": "Intercape Zimbabwe",
        "category_slug": "cross-border",
        "name": "Intercape Sleepliner — Harare to Johannesburg",
        "fare_gazetted": 45.00,
        "fare_estimate": 50.00,
        "source_url": "https://www.intercape.co.za/routes/harare-johannesburg",
        "description": "Cross-border sleeper coach with climate control and 150-degree reclining memory foam seats",
        "attributes": {
            "service_level": "Sleepliner",
            "fare_gazetted": 45.00,
            "fare_estimate": 50.00,
            "fleet_type": "Coach",
            "province_district": "Harare — Johannesburg",
            "ownership_status": "private",
            "urbanicity": "both",
            "passenger_or_freight": "passenger"
        }
    },
    # Contract / Staff - ZUPCO
    {
        "provider": "ZUPCO - Staff Bus Contract",
        "category_slug": "contract-staff",
        "name": "ZUPCO Dedicated Industrial Staff Transport",
        "fare_gazetted": 2.00,
        "fare_estimate": 2.00,
        "source_url": "https://www.zupco.co.zw/charter",
        "description": "Contracted dedicated workforce commute bus service",
        "attributes": {
            "service_level": "Contract",
            "fare_gazetted": 2.00,
            "fare_estimate": 2.00,
            "fleet_type": "Bus",
            "province_district": "Harare Industrial Sites",
            "ownership_status": "state",
            "urbanicity": "urban",
            "passenger_or_freight": "passenger"
        }
    }
]


def seed_transport_sector(db=None):
    """Seed Transport sector, 8 transport categories, 16-field schema, operators, and listings."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        print("[Transport Seed] Starting Transport Sector database seed...")

        # 1. Ensure Transport sector exists and is LIVE
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "transport").first()
        if not sector:
            sector = SectorConfig(
                id=_uid(),
                name="Transport",
                slug="transport",
                status=SectorStatus.LIVE,
                icon="bus",
                blurb="Compare urban kombi fares, intercity coaches, air travel, freight, and ride-hailing services"
            )
            db.add(sector)
            db.flush()
            print("  [+] Created Sector: Transport")
        else:
            sector.name = "Transport"
            sector.status = SectorStatus.LIVE
            db.flush()

        # 2. Seed All 8 Categories & 16-Field Attribute Schema
        cat_map = {}
        for cat_spec in TRANSPORT_CATEGORIES:
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

            # Upsert all 16 schema fields for this category
            for f in COMMON_TRANSPORT_FIELDS:
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

        # 3. Seed Transport Operators (Providers)
        provider_map = {}
        for p_data in TRANSPORT_PROVIDERS:
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
                print(f"  [+] Transport Provider: {provider.name}")
            else:
                provider.website_url = p_data.get("website_url")
                provider.corporate_domain = p_data.get("corporate_domain")
                provider.description = p_data.get("description")
                db.flush()
            provider_map[p_data["name"]] = provider

        # 4. Seed Transport Service Listings
        now = datetime.utcnow()
        for item in SAMPLE_TRANSPORT_LISTINGS:
            cat = cat_map.get(item["category_slug"])
            provider = provider_map.get(item["provider"])
            if not cat or not provider:
                continue

            # Determine price: fare_gazetted preferred, else fare_estimate
            price_val = float(item["fare_gazetted"] if item.get("fare_gazetted") is not None else item["fare_estimate"])

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
                    price=price_val,
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
                    price=price_val,
                    currency="USD",
                    recorded_at=now
                )
                db.add(hist)
            else:
                listing.price = price_val
                listing.attributes = item.get("attributes", {})
                listing.source_url = item.get("source_url")
                listing.last_verified_at = now

        db.commit()
        print(f"[Transport Seed] Successfully seeded {len(TRANSPORT_CATEGORIES)} categories with 16-field schemas, operators, and listings!")
    except Exception as e:
        db.rollback()
        print(f"[Transport Seed] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_transport_sector()
