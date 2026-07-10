from app.db.session import SessionLocal
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.source import Source
from app.db.models.source_page import SourcePage
from app.services.extractor import ExtractorService
from sqlalchemy import text

def reparse():
    db = SessionLocal()
    extractor_service = ExtractorService(db)
    
    # Get ALL snapshots
    snapshots = db.query(RawSnapshot).order_by(RawSnapshot.id.desc()).all()
    print(f"Reparsing {len(snapshots)} snapshots...")
    
    for snapshot in snapshots:
        try:
            # Correctly get category
            cat = "unknown"
            if snapshot.source_page_id:
                source = db.query(Source).join(SourcePage).filter(SourcePage.id == snapshot.source_page_id).first()
                if source:
                    cat = source.category
            
            print(f"Processing snapshot {snapshot.id} ({cat}) for {snapshot.url}")
            
            # Clear existing records for this snapshot
            db.query(ExtractedRecord).filter(ExtractedRecord.snapshot_id == snapshot.id).delete()
            db.commit()
            
            # Extract again
            records = extractor_service.extract_from_snapshot(snapshot)
            print(f"  -> Extracted {len(records)} records")
        except Exception as e:
            print(f"Error processing snapshot {snapshot.id}: {e}")
            db.rollback()

    db.close()
    print("Reparse complete.")

if __name__ == "__main__":
    reparse()
