from app.db.session import get_db_session
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.extracted_record import ExtractedRecord
from datetime import datetime

# Sample HTML content for testing
sample_html = """
<html>
<head><title>Test Telecom Page</title></head>
<body>
    <h1>Mobile Phone Plans</h1>
    <div class="plan">
        <h2>Unlimited Plan</h2>
        <p>Price: £25/month</p>
        <p>Data: Unlimited</p>
    </div>
    <div class="plan">
        <h2>100GB Plan</h2>
        <p>Price: £20/month</p>
        <p>Data: 100GB</p>
    </div>
</body>
</html>
"""

def create_sample_data():
    db = next(get_db_session())
    try:
        # Create a sample snapshot
        snapshot = RawSnapshot(
            source_page_id=None,
            url="https://example.com/test-plans",
            content=sample_html,
            content_type="html"
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        # Create sample extracted records
        records_data = [
            {
                "snapshot_id": snapshot.id,
                "entity_name": "Test Telecom",
                "category": "telecom",
                "subcategory": "mobile_plan",
                "title": "Unlimited Plan",
                "item_name": "Unlimited Mobile Plan",
                "description": "Unlimited data mobile plan",
                "price_value": 25.00,
                "price_currency": "GBP",
                "billing_period": "monthly",
                "source_url": "https://example.com/test-plans"
            },
            {
                "snapshot_id": snapshot.id,
                "entity_name": "Test Telecom",
                "category": "telecom",
                "subcategory": "mobile_plan",
                "title": "100GB Plan",
                "item_name": "100GB Mobile Plan",
                "description": "100GB data mobile plan",
                "price_value": 20.00,
                "price_currency": "GBP",
                "billing_period": "monthly",
                "source_url": "https://example.com/test-plans"
            },
            {
                "snapshot_id": snapshot.id,
                "entity_name": "Test Bank",
                "category": "banking",
                "subcategory": "current_account",
                "title": "Current Account",
                "item_name": "Standard Current Account",
                "description": "Standard current account with no monthly fees",
                "price_value": 0.00,
                "price_currency": "GBP",
                "billing_period": "monthly",
                "source_url": "https://example.com/test-accounts"
            }
        ]

        for record_data in records_data:
            record = ExtractedRecord(**record_data)
            db.add(record)

        db.commit()
        print(f"Created 1 snapshot and {len(records_data)} extracted records")

    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()