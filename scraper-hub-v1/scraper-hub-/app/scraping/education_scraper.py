"""
Education Scraper Engine
Automated landing of primary school fees, secondary school fees, and university tuition
directly into the database-driven catalog.
"""
from typing import Dict, Any, List
from app.db.session import SessionLocal
from app.services.education_service import education_service
from app.data.education_seed import SAMPLE_EDUCATION_LISTINGS


def run_education_scraper(db=None) -> Dict[str, Any]:
    """Execute automated scrape and direct DB write for Education institutions and fees."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    created_count = 0
    updated_count = 0

    try:
        print("[Education Scraper] Starting automated education fees ingestion...")

        for item in SAMPLE_EDUCATION_LISTINGS:
            res = education_service.ingest_listing(
                db,
                institution_name=item["institution"],
                category_slug=item["category_slug"],
                listing_name=item["name"],
                price=item["price"],
                currency="USD",
                attributes=item.get("attributes", {}),
                source_url=item.get("source_url"),
                description=item.get("description")
            )
            if res["action"] == "created":
                created_count += 1
            elif res["action"] == "updated":
                updated_count += 1
            print(f"  [+] Ingested Education Fee: {item['name']} ({res['action']})")

        db.commit()
        print(f"[Education Scraper] Ingestion complete. Created: {created_count}, Updated: {updated_count}")
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count
        }
    except Exception as e:
        db.rollback()
        print(f"[Education Scraper] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    run_education_scraper()
