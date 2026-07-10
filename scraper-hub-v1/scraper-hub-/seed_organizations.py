"""
seed_organizations.py — Seeds all Zimbabwe organizations into the database.
Safe to re-run (idempotent): skips existing records by slug.

Usage:
    .\\venv_new\\Scripts\\python.exe seed_organizations.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.data.zimbabwe_organizations import get_all_organizations


def seed():
    db = SessionLocal()
    orgs = get_all_organizations()
    added = 0
    skipped = 0

    try:
        for org_data in orgs:
            existing = db.query(Organization).filter(
                Organization.slug == org_data["slug"]
            ).first()

            if existing:
                skipped += 1
                continue

            org = Organization(
                name=org_data["name"],
                slug=org_data["slug"],
                category=org_data["category"],
                website=org_data.get("website"),
                industry_tags=json.dumps(org_data.get("industry_tags", [])),
                keywords=json.dumps(org_data.get("keywords", [])),
                registration_status=org_data.get("registration_status", "active"),
                scrape_status=org_data.get("scrape_status", "pending"),
                data_completeness=org_data.get("data_completeness", 5.0),
            )
            db.add(org)
            added += 1

        db.commit()
        print(f"\n✅ Done! Added: {added}  |  Skipped (already exist): {skipped}")
        print(f"   Total organizations in DB: {added + skipped}")

        # Print breakdown by category
        from sqlalchemy import func
        cats = db.query(Organization.category, func.count(Organization.id))\
                 .group_by(Organization.category)\
                 .order_by(Organization.category)\
                 .all()
        print("\n📊 Breakdown by category:")
        for cat, count in cats:
            print(f"   {cat:<30} {count}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding Zimbabwe organizations...")
    seed()
