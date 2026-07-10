import asyncio
from app.db.session import SessionLocal
from app.services.fetcher import PlaywrightFetcher
from app.services.extractor import ExtractorService
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.source import Source

async def test_extract():
    snapshot_id = 373 # Cresta Lodge Harare

    print(f"Testing extraction for snapshot {snapshot_id}")
    
    db = SessionLocal()
    extractor_service = ExtractorService(db)
    
    try:
        snapshot = db.query(RawSnapshot).filter(RawSnapshot.id == snapshot_id).first()
        if not snapshot:
            print(f"Snapshot {snapshot_id} not found")
            return
            
        print(f"Snapshot URL: {snapshot.url}")
        
        records = extractor_service.extract_from_snapshot(snapshot)
        print(f"Extracted {len(records)} records")
        for r in records:
            print(f"Entity: {r['entity_name']} | Title: {r['title']} | Price: {r['price_currency']}{r['price_value']}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_extract())
