"""
Hotels Scraper Engine
Automated landing of Zimbabwean hotel room rates, safari lodge packages,
and suites directly into the database catalog.
"""
from typing import Dict, Any
from app.db.session import SessionLocal
from app.services.hotels_service import hotels_service
from app.data.hotels_seed import SAMPLE_HOTEL_LISTINGS


def run_hotels_scraper(db=None) -> Dict[str, Any]:
    """Execute automated scrape and direct DB write for Hotel room rates."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    created_count = 0
    updated_count = 0

    try:
        print("[Hotels Scraper] Starting automated Hotels room rates ingestion...")

        for item in SAMPLE_HOTEL_LISTINGS:
            res = hotels_service.ingest_room_listing(
                db,
                hotel_name=item["hotel"],
                room_name=item["name"],
                price_per_night=item["price"],
                currency="USD",
                attributes=item.get("attributes", {}),
                source_url=item.get("source_url"),
                description=item.get("description")
            )
            if res["action"] == "created":
                created_count += 1
            elif res["action"] == "updated":
                updated_count += 1
            print(f"  [+] Ingested Hotel Room: {item['name']} ({res['action']})")

        db.commit()
        print(f"[Hotels Scraper] Ingestion complete. Created: {created_count}, Updated: {updated_count}")
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count
        }
    except Exception as e:
        db.rollback()
        print(f"[Hotels Scraper] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    run_hotels_scraper()
