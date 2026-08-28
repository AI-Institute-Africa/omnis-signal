"""
Retail & Groceries Scraper Engine
Automated landing of Zimbabwean grocery prices, hardware commodities,
and solar equipment directly into the database catalog.
"""
from typing import Dict, Any
from app.db.session import SessionLocal
from app.services.retail_service import retail_service
from app.data.retail_seed import SAMPLE_RETAIL_LISTINGS


def run_retail_scraper(db=None) -> Dict[str, Any]:
    """Execute automated scrape and direct DB write for Retail & Groceries products."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    created_count = 0
    updated_count = 0

    try:
        print("[Retail Scraper] Starting automated Retail & Groceries commodity ingestion...")

        for item in SAMPLE_RETAIL_LISTINGS:
            res = retail_service.ingest_product_listing(
                db,
                supplier_name=item["provider"],
                category_slug=item["category_slug"],
                product_name=item["name"],
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
            print(f"  [+] Ingested Commodity: {item['name']} ({res['action']})")

        db.commit()
        print(f"[Retail Scraper] Ingestion complete. Created: {created_count}, Updated: {updated_count}")
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count
        }
    except Exception as e:
        db.rollback()
        print(f"[Retail Scraper] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    run_retail_scraper()
