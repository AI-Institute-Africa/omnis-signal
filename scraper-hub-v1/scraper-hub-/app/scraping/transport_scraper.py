"""
Transport Scraper Engine
Automated landing of Zimbabwean urban commuter kombis, intercity coaches,
air travel, and ride-hailing services directly into the database catalog.
"""
from typing import Dict, Any
from app.db.session import SessionLocal
from app.services.transport_service import transport_service
from app.data.transport_seed import SAMPLE_TRANSPORT_LISTINGS


def run_transport_scraper(db=None) -> Dict[str, Any]:
    """Execute automated scrape and direct DB write for Transport services."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    created_count = 0
    updated_count = 0

    try:
        print("[Transport Scraper] Starting automated Transport service ingestion...")

        for item in SAMPLE_TRANSPORT_LISTINGS:
            res = transport_service.ingest_transport_listing(
                db,
                operator_name=item["provider"],
                category_slug=item["category_slug"],
                service_name=item["name"],
                fare_gazetted=item.get("fare_gazetted"),
                fare_estimate=item.get("fare_estimate"),
                currency="USD",
                attributes=item.get("attributes", {}),
                source_url=item.get("source_url"),
                description=item.get("description")
            )
            if res["action"] == "created":
                created_count += 1
            elif res["action"] == "updated":
                updated_count += 1
            print(f"  [+] Ingested Transport Route: {item['name']} ({res['action']})")

        db.commit()
        print(f"[Transport Scraper] Ingestion complete. Created: {created_count}, Updated: {updated_count}")
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count
        }
    except Exception as e:
        db.rollback()
        print(f"[Transport Scraper] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    run_transport_scraper()
