import sys
from app.db.session import SessionLocal
from app.db.models.raw_snapshot import RawSnapshot
from app.services.extractor import ExtractorService
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.product import Product
from app.db.models.service import Service
from app.db.models.price_entry import PriceEntry

def reprocess(snapshot_id):
    db = SessionLocal()
    try:
        snapshot = db.query(RawSnapshot).filter(RawSnapshot.id == snapshot_id).first()
        if not snapshot:
            print(f"Snapshot {snapshot_id} not found.")
            return

        print(f"Reprocessing snapshot {snapshot.id} for {snapshot.url}...")
        
        # Clear existing associations to this snapshot to avoid duplicates if necessary
        # However, ExtractorService handles some of this. 
        # For a clean test, let's just run it.
        
        extractor_service = ExtractorService(db)
        created_records = extractor_service.extract_from_snapshot(snapshot)
        
        print(f"Extraction complete. Created/Updated {len(created_records)} records.")
        
        # Now fetch the records and their price entries to show the new fields
        for rec in created_records:
            # Note: created_records are dicts from extractor_service
            print(f"\nRecord: {rec['title']}")
            print(f"  Category: {rec['category']}")
            
            # Fetch from DB to see subcategory and normalized data
            # Check extracted_records table (older structure) or product/service (newer structure)
            # Since IntelligenceService was called, it should be in product/service
            
            p = db.query(Product).filter(Product.name == rec['title']).first()
            s = db.query(Service).filter(Service.name == rec['title']).first()
            
            item = p or s
            if item:
                print(f"  Subcategory: {item.subcategory}")
                latest_price = db.query(PriceEntry).filter(
                    (PriceEntry.product_id == item.id) if p else (PriceEntry.service_id == item.id)
                ).order_by(PriceEntry.captured_at.desc()).first()
                
                if latest_price:
                    print(f"  Normalized Value: {latest_price.normalized_value} {latest_price.normalized_unit}")
                    print(f"  Formula: {latest_price.formula}")
                    print(f"  Monthly: {latest_price.monthly}, Daily: {latest_price.daily}")
            else:
                print("  (Item not found in Product/Service tables yet)")

    finally:
        db.close()

if __name__ == "__main__":
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 1001
    reprocess(sid)
