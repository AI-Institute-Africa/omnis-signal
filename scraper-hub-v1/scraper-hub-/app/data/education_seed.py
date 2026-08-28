"""
Education Sector Database Seed
Implements:
1. Sector: education
2. Categories: primary-schools, secondary-schools, universities
3. Attribute schema fields with normalisation contracts
4. Seed institutions (Providers) & sample fee listings
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
# 1. EDUCATION CATEGORIES & ATTRIBUTE SCHEMAS
# ============================================================================
EDUCATION_CATEGORIES = [
    {
        "slug": "primary-schools",
        "name": "Primary schools",
        "synonyms": ["primary school", "prep school", "grade 1-7", "junior school"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "term_fees", "label": "Term fees", "consumer_label": "Fee per term", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 0},
            {"key": "curriculum", "label": "Curriculum", "consumer_label": "Curriculum type (Zimbabwe, Cambridge, IB, other)", "data_type": AttributeDataType.ENUM, "unit": None, "sort_order": 1},
            {"key": "boarding", "label": "Boarding", "consumer_label": "Boarding facility available", "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 2},
            {"key": "student_teacher_ratio", "label": "Student:teacher ratio", "consumer_label": "Class ratio", "data_type": AttributeDataType.NUMBER, "unit": None, "sort_order": 3},
            {"key": "location", "label": "Location", "consumer_label": "City / Suburb", "data_type": AttributeDataType.STRING, "unit": None, "sort_order": 4},
        ]
    },
    {
        "slug": "secondary-schools",
        "name": "Secondary schools",
        "synonyms": ["secondary school", "high school", "form 1-6", "college"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "term_fees", "label": "Term fees", "consumer_label": "Fee per term", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 0},
            {"key": "curriculum", "label": "Curriculum", "consumer_label": "Curriculum type (Zimbabwe, Cambridge, IB, other)", "data_type": AttributeDataType.ENUM, "unit": None, "sort_order": 1},
            {"key": "boarding", "label": "Boarding", "consumer_label": "Boarding school", "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 2},
            {"key": "pass_rate_pct", "label": "Pass rate", "consumer_label": "O/A Level pass rate %", "data_type": AttributeDataType.NUMBER, "unit": "%", "sort_order": 3},
            {"key": "location", "label": "Location", "consumer_label": "City / Province", "data_type": AttributeDataType.STRING, "unit": None, "sort_order": 4},
        ]
    },
    {
        "slug": "universities",
        "name": "Universities & tertiary",
        "synonyms": ["university", "tertiary", "college", "higher education", "polytechnic"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "tuition_per_year", "label": "Tuition (per year)", "consumer_label": "Annual tuition fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 0},
            {"key": "program_count", "label": "Programmes", "consumer_label": "Number of degree programmes offered", "data_type": AttributeDataType.NUMBER, "unit": None, "sort_order": 1},
            {"key": "residential", "label": "On-campus accommodation", "consumer_label": "Campus housing available", "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 2},
            {"key": "study_mode", "label": "Study mode", "consumer_label": "full_time, part_time, distance, blended", "data_type": AttributeDataType.ENUM, "unit": None, "sort_order": 3},
            {"key": "location", "label": "Location", "consumer_label": "Campus city", "data_type": AttributeDataType.STRING, "unit": None, "sort_order": 4},
        ]
    }
]


# ============================================================================
# 2. SEED INSTITUTIONS (PROVIDERS)
# ============================================================================
EDUCATION_PROVIDERS = [
    # Primary Schools
    {
        "name": "Chisipite Junior",
        "category": "primary-schools",
        "website_url": "https://www.chisipitejunior.com",
        "corporate_domain": "chisipitejunior.com",
        "description": "Girls private primary school in Harare"
    },
    {
        "name": "Hartmann House",
        "category": "primary-schools",
        "website_url": "https://www.hartmannhouse.co.zw",
        "corporate_domain": "hartmannhouse.co.zw",
        "description": "Jesuit preparatory primary school for boys in Harare"
    },
    {
        "name": "Coghlan Primary",
        "category": "primary-schools",
        "website_url": "https://www.coghlanprimary.ac.zw",
        "corporate_domain": "coghlanprimary.ac.zw",
        "description": "Government primary school in Bulawayo"
    },
    {
        "name": "Whitestone Primary",
        "category": "primary-schools",
        "website_url": "https://www.whitestone.ac.zw",
        "corporate_domain": "whitestone.ac.zw",
        "description": "Co-educational private boarding and day primary school in Bulawayo"
    },

    # Secondary Schools
    {
        "name": "Peterhouse",
        "category": "secondary-schools",
        "website_url": "https://www.peterhouse.co.zw",
        "corporate_domain": "peterhouse.co.zw",
        "description": "Group of independent boarding high schools in Marondera"
    },
    {
        "name": "St George's College",
        "category": "secondary-schools",
        "website_url": "https://www.stgeorges.co.zw",
        "corporate_domain": "stgeorges.co.zw",
        "description": "Catholic Jesuit boys independent high school in Harare"
    },
    {
        "name": "Founders High",
        "category": "secondary-schools",
        "website_url": "https://www.foundershigh.ac.zw",
        "corporate_domain": "foundershigh.ac.zw",
        "description": "Government secondary school in Bulawayo"
    },
    {
        "name": "Girls High School",
        "category": "secondary-schools",
        "website_url": "https://www.girlshighharare.ac.zw",
        "corporate_domain": "girlshighharare.ac.zw",
        "description": "Leading government girls secondary school in Harare"
    },
    {
        "name": "Trinity College",
        "category": "secondary-schools",
        "website_url": "https://www.trinitycollege.ac.zw",
        "corporate_domain": "trinitycollege.ac.zw",
        "description": "Independent high school in Harare offering Cambridge and ZIMSEC"
    },

    # Universities & Tertiary
    {
        "name": "University of Zimbabwe",
        "category": "universities",
        "website_url": "https://www.uz.ac.zw",
        "corporate_domain": "uz.ac.zw",
        "description": "Premier national public research university in Harare"
    },
    {
        "name": "NUST",
        "category": "universities",
        "website_url": "https://www.nust.ac.zw",
        "corporate_domain": "nust.ac.zw",
        "description": "National University of Science and Technology in Bulawayo"
    },
    {
        "name": "Midlands State University",
        "category": "universities",
        "website_url": "https://www.msu.ac.zw",
        "corporate_domain": "msu.ac.zw",
        "description": "Multi-campus state research university based in Gweru"
    },
    {
        "name": "Harare Institute of Technology",
        "category": "universities",
        "website_url": "https://www.hit.ac.zw",
        "corporate_domain": "hit.ac.zw",
        "description": "State university focused on technology, engineering, and innovation"
    },
    {
        "name": "Great Zimbabwe University",
        "category": "universities",
        "website_url": "https://www.gzu.ac.zw",
        "corporate_domain": "gzu.ac.zw",
        "description": "State university situated in Masvingo"
    },
    {
        "name": "Chinhoyi University of Technology",
        "category": "universities",
        "website_url": "https://www.cut.ac.zw",
        "corporate_domain": "cut.ac.zw",
        "description": "State university in Chinhoyi focused on technology and hospitality"
    }
]


# ============================================================================
# 3. SAMPLE EDUCATION FEE LISTINGS
# ============================================================================
SAMPLE_EDUCATION_LISTINGS = [
    # Primary Schools
    {
        "institution": "Chisipite Junior",
        "category_slug": "primary-schools",
        "name": "Chisipite Junior — Grade 1-7 Day Tuition",
        "price": 1450.00,
        "source_url": "https://www.chisipitejunior.com/fees",
        "description": "Tuition per term for Junior School Day Scholars",
        "attributes": {
            "term_fees": 1450.00,
            "curriculum": "Cambridge",
            "boarding": False,
            "student_teacher_ratio": 18,
            "location": "Harare"
        }
    },
    {
        "institution": "Hartmann House",
        "category_slug": "primary-schools",
        "name": "Hartmann House — Grade 1-7 Tuition",
        "price": 1300.00,
        "source_url": "https://www.hartmannhouse.co.zw/fees",
        "description": "Prep school tuition per term",
        "attributes": {
            "term_fees": 1300.00,
            "curriculum": "Cambridge",
            "boarding": False,
            "student_teacher_ratio": 20,
            "location": "Harare"
        }
    },
    {
        "institution": "Whitestone Primary",
        "category_slug": "primary-schools",
        "name": "Whitestone Primary — Grade 1-7 Boarding & Tuition",
        "price": 1950.00,
        "source_url": "https://www.whitestone.ac.zw/fees",
        "description": "Full boarding and tuition per term",
        "attributes": {
            "term_fees": 1950.00,
            "curriculum": "Cambridge",
            "boarding": True,
            "student_teacher_ratio": 16,
            "location": "Bulawayo"
        }
    },
    {
        "institution": "Coghlan Primary",
        "category_slug": "primary-schools",
        "name": "Coghlan Primary — Day Scholar Levy & Tuition",
        "price": 120.00,
        "source_url": "https://www.coghlanprimary.ac.zw/fees",
        "description": "Government school term fee",
        "attributes": {
            "term_fees": 120.00,
            "curriculum": "Zimbabwe",
            "boarding": False,
            "student_teacher_ratio": 35,
            "location": "Bulawayo"
        }
    },

    # Secondary Schools
    {
        "institution": "Peterhouse",
        "category_slug": "secondary-schools",
        "name": "Peterhouse — Form 1-4 Boarding & Tuition",
        "price": 2400.00,
        "source_url": "https://www.peterhouse.co.zw/fees",
        "description": "Full boarding and academic tuition for junior secondary per term",
        "attributes": {
            "term_fees": 2400.00,
            "curriculum": "Cambridge",
            "boarding": True,
            "pass_rate_pct": 92.5,
            "location": "Marondera"
        }
    },
    {
        "institution": "Peterhouse",
        "category_slug": "secondary-schools",
        "name": "Peterhouse — Sixth Form (A-Level) Boarding",
        "price": 2750.00,
        "source_url": "https://www.peterhouse.co.zw/fees",
        "description": "Sixth form A-Level boarding fees per term",
        "attributes": {
            "term_fees": 2750.00,
            "curriculum": "Cambridge",
            "boarding": True,
            "pass_rate_pct": 96.0,
            "location": "Marondera"
        }
    },
    {
        "institution": "St George's College",
        "category_slug": "secondary-schools",
        "name": "St George's College — Form 1-6 Day Tuition",
        "price": 1800.00,
        "source_url": "https://www.stgeorges.co.zw/fees",
        "description": "Senior school academic tuition per term",
        "attributes": {
            "term_fees": 1800.00,
            "curriculum": "Cambridge",
            "boarding": False,
            "pass_rate_pct": 94.0,
            "location": "Harare"
        }
    },
    {
        "institution": "Girls High School",
        "category_slug": "secondary-schools",
        "name": "Girls High School — Form 1-4 Day Tuition & Levy",
        "price": 250.00,
        "source_url": "https://www.girlshighharare.ac.zw/fees",
        "description": "Government secondary school term tuition and SDC levy",
        "attributes": {
            "term_fees": 250.00,
            "curriculum": "Zimbabwe",
            "boarding": False,
            "pass_rate_pct": 86.0,
            "location": "Harare"
        }
    },
    {
        "institution": "Trinity College",
        "category_slug": "secondary-schools",
        "name": "Trinity College — Form 1-6 Tuition",
        "price": 850.00,
        "source_url": "https://www.trinitycollege.ac.zw/fees",
        "description": "Private day high school fees",
        "attributes": {
            "term_fees": 850.00,
            "curriculum": "Cambridge",
            "boarding": False,
            "pass_rate_pct": 89.0,
            "location": "Harare"
        }
    },

    # Universities & Tertiary
    {
        "institution": "University of Zimbabwe",
        "category_slug": "universities",
        "name": "University of Zimbabwe — Faculty of Engineering (per year)",
        "price": 1200.00,
        "source_url": "https://www.uz.ac.zw/fees",
        "description": "Undergraduate B.Sc Engineering annual tuition",
        "attributes": {
            "tuition_per_year": 1200.00,
            "program_count": 120,
            "residential": True,
            "study_mode": "full_time",
            "location": "Harare"
        }
    },
    {
        "institution": "University of Zimbabwe",
        "category_slug": "universities",
        "name": "University of Zimbabwe — Faculty of Medicine (per year)",
        "price": 1600.00,
        "source_url": "https://www.uz.ac.zw/fees",
        "description": "Undergraduate MBChB Medicine & Surgery annual tuition",
        "attributes": {
            "tuition_per_year": 1600.00,
            "program_count": 120,
            "residential": True,
            "study_mode": "full_time",
            "location": "Harare"
        }
    },
    {
        "institution": "University of Zimbabwe",
        "category_slug": "universities",
        "name": "University of Zimbabwe — Faculty of Commerce (per year)",
        "price": 950.00,
        "source_url": "https://www.uz.ac.zw/fees",
        "description": "Undergraduate Business & Accounting annual tuition",
        "attributes": {
            "tuition_per_year": 950.00,
            "program_count": 120,
            "residential": True,
            "study_mode": "blended",
            "location": "Harare"
        }
    },
    {
        "institution": "NUST",
        "category_slug": "universities",
        "name": "NUST — Computer Science & Software Engineering (per year)",
        "price": 1100.00,
        "source_url": "https://www.nust.ac.zw/fees",
        "description": "B.Sc Computer Science annual tuition",
        "attributes": {
            "tuition_per_year": 1100.00,
            "program_count": 85,
            "residential": True,
            "study_mode": "full_time",
            "location": "Bulawayo"
        }
    },
    {
        "institution": "Midlands State University",
        "category_slug": "universities",
        "name": "Midlands State University — Law & Social Sciences (per year)",
        "price": 1050.00,
        "source_url": "https://www.msu.ac.zw/fees",
        "description": "Undergraduate Bachelor of Laws (LL.B) annual tuition",
        "attributes": {
            "tuition_per_year": 1050.00,
            "program_count": 140,
            "residential": True,
            "study_mode": "blended",
            "location": "Gweru"
        }
    },
    {
        "institution": "Harare Institute of Technology",
        "category_slug": "universities",
        "name": "Harare Institute of Technology — Information Technology (per year)",
        "price": 1000.00,
        "source_url": "https://www.hit.ac.zw/fees",
        "description": "B.Tech Information Technology annual tuition",
        "attributes": {
            "tuition_per_year": 1000.00,
            "program_count": 45,
            "residential": True,
            "study_mode": "full_time",
            "location": "Harare"
        }
    },
    {
        "institution": "Chinhoyi University of Technology",
        "category_slug": "universities",
        "name": "Chinhoyi University of Technology — Hospitality & Tourism (per year)",
        "price": 900.00,
        "source_url": "https://www.cut.ac.zw/fees",
        "description": "B.Sc Hospitality and Tourism Management annual tuition",
        "attributes": {
            "tuition_per_year": 900.00,
            "program_count": 60,
            "residential": True,
            "study_mode": "full_time",
            "location": "Chinhoyi"
        }
    }
]


def seed_education_sector(db=None):
    """Seed Education sector, categories, attribute schemas, institutions, and listings."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        print("[Education Seed] Starting Education Sector database seed...")

        # 1. Ensure Education sector exists and is LIVE
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "education").first()
        if not sector:
            sector = SectorConfig(
                id=_uid(),
                name="Education",
                slug="education",
                status=SectorStatus.LIVE,
                icon="graduation-cap",
                blurb="Compare school fees, university tuition, boarding and academic programmes"
            )
            db.add(sector)
            db.flush()
            print("  [+] Created Sector: Education")
        else:
            sector.status = SectorStatus.LIVE
            db.flush()

        # 2. Seed 3 Categories & Attribute Schemas
        cat_map = {}
        for cat_spec in EDUCATION_CATEGORIES:
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
                    attr.is_comparable = True

        # 3. Seed Institutions (Providers)
        provider_map = {}
        for p_data in EDUCATION_PROVIDERS:
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
                print(f"  [+] Institution: {provider.name}")
            else:
                provider.website_url = p_data.get("website_url")
                provider.corporate_domain = p_data.get("corporate_domain")
                provider.description = p_data.get("description")
                db.flush()
            provider_map[p_data["name"]] = provider

        # 4. Seed Education Listings
        now = datetime.utcnow()
        for item in SAMPLE_EDUCATION_LISTINGS:
            cat = cat_map.get(item["category_slug"])
            provider = provider_map.get(item["institution"])
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
        print("[Education Seed] Successfully seeded Education sector, categories, institutions, and fee listings!")
    except Exception as e:
        db.rollback()
        print(f"[Education Seed] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_education_sector()
