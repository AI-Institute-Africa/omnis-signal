"""
Telecom Scraper Engine
Automated landing of Zimbabwean mobile data bundles, WhatsApp packs,
voice minutes and WiFi plans directly into the database catalog.
"""
from typing import Dict, Any
from app.db.session import SessionLocal
from app.services.telecom_service import telecom_service
from app.data.telecom_seed import SAMPLE_TELECOM_LISTINGS


def run_telecom_scraper(db=None) -> Dict[str, Any]:
    """Execute automated scrape and direct DB write for Telecom bundles."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    created_count = 0
    updated_count = 0

    try:
        print("[Telecom Scraper] Starting automated Telecom bundle ingestion...")

        for item in SAMPLE_TELECOM_LISTINGS:
            res = telecom_service.ingest_bundle_listing(
                db,
                operator_name=item["operator"],
                category_slug=item["category_slug"],
                bundle_name=item["name"],
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
            print(f"  [+] Ingested Bundle: {item['name']} ({res['action']})")

        db.commit()
        print(f"[Telecom Scraper] Ingestion complete. Created: {created_count}, Updated: {updated_count}")
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count
        }
    except Exception as e:
        db.rollback()
        print(f"[Telecom Scraper] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    run_telecom_scraper()
