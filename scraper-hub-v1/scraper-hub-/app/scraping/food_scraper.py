"""
Food & Drink Scraper Engine
Automated landing of Zimbabwean restaurant menu items, meal combos,
and casual dining prices directly into the database catalog.
"""
from typing import Dict, Any
from app.db.session import SessionLocal
from app.services.food_service import food_service
from app.data.food_seed import SAMPLE_FOOD_LISTINGS


def run_food_scraper(db=None) -> Dict[str, Any]:
    """Execute automated scrape and direct DB write for Food & Drink menu items."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    created_count = 0
    updated_count = 0

    try:
        print("[Food Scraper] Starting automated Food & Drink menu ingestion...")

        for item in SAMPLE_FOOD_LISTINGS:
            res = food_service.ingest_menu_item(
                db,
                restaurant_name=item["restaurant"],
                category_slug=item["category_slug"],
                menu_item_name=item["name"],
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
            print(f"  [+] Ingested Menu Item: {item['name']} ({res['action']})")

        db.commit()
        print(f"[Food Scraper] Ingestion complete. Created: {created_count}, Updated: {updated_count}")
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count
        }
    except Exception as e:
        db.rollback()
        print(f"[Food Scraper] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    run_food_scraper()
