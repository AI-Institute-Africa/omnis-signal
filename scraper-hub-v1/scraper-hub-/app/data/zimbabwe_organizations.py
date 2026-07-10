"""
Zimbabwe organizations master catalog.
Combines all sectors: banks, hotels, telecoms, mobility, universities,
colleges, schools, insurance, solar, transport, utilities.
"""
import re
from app.data.zimbabwe_orgs_p1 import ORGANIZATIONS as P1
from app.data.zimbabwe_orgs_p2 import ORGANIZATIONS_P2 as P2


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s.strip())
    return s[:120]


ALL_ORGANIZATIONS = P1 + P2


CATEGORY_META = {
    "banks": {
        "label": "Banks & Financial",
        "icon": "🏦",
        "color": "#2563eb",
        "industry_tags": ["banking", "finance", "financial services"],
    },
    "hotels": {
        "label": "Hotels & Hospitality",
        "icon": "🏨",
        "color": "#d97706",
        "industry_tags": ["hospitality", "tourism", "accommodation"],
    },
    "telecoms": {
        "label": "Telecoms & Internet",
        "icon": "📡",
        "color": "#7c3aed",
        "industry_tags": ["telecommunications", "internet", "mobile"],
    },
    "mobility": {
        "label": "Mobility & Transport Tech",
        "icon": "🚗",
        "color": "#059669",
        "industry_tags": ["mobility", "ride-hailing", "transport technology"],
    },
    "universities": {
        "label": "Universities",
        "icon": "🎓",
        "color": "#dc2626",
        "industry_tags": ["higher education", "research", "academia"],
    },
    "colleges": {
        "label": "Colleges & Vocational",
        "icon": "📚",
        "color": "#0891b2",
        "industry_tags": ["education", "vocational training", "polytechnic"],
    },
    "schools": {
        "label": "Schools",
        "icon": "🏫",
        "color": "#65a30d",
        "industry_tags": ["education", "secondary school", "primary school"],
    },
    "insurance": {
        "label": "Insurance",
        "icon": "🛡️",
        "color": "#9333ea",
        "industry_tags": ["insurance", "assurance", "risk management"],
    },
    "solar": {
        "label": "Solar & Renewable Energy",
        "icon": "☀️",
        "color": "#f59e0b",
        "industry_tags": ["solar energy", "renewable energy", "green tech"],
    },
    "transport": {
        "label": "Transport & Logistics",
        "icon": "🚛",
        "color": "#6b7280",
        "industry_tags": ["logistics", "freight", "courier", "bus services"],
    },
    "utilities": {
        "label": "Utilities",
        "icon": "⚡",
        "color": "#1d4ed8",
        "industry_tags": ["electricity", "water", "fuel", "energy"],
    },
}


def get_all_organizations():
    """Return all organizations with computed slugs and enriched metadata."""
    result = []
    seen_slugs = {}
    for org in ALL_ORGANIZATIONS:
        base_slug = slugify(org["name"])
        count = seen_slugs.get(base_slug, 0)
        slug = base_slug if count == 0 else f"{base_slug}-{count}"
        seen_slugs[base_slug] = count + 1

        cat = org.get("category", "other")
        meta = CATEGORY_META.get(cat, {})
        tags = meta.get("industry_tags", []) + org.get("keywords", [])

        result.append({
            **org,
            "slug": slug,
            "industry_tags": list(set(tags)),
            "registration_status": "active",
            "scrape_status": "pending",
            "data_completeness": 5.0,  # starts low, gets filled by scrapers
        })
    return result


def get_categories():
    return CATEGORY_META


def get_by_category(category: str):
    return [o for o in get_all_organizations() if o["category"] == category]
