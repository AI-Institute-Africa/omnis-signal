import asyncio
import logging
from app.db.session import SessionLocal
from app.services.fetcher import PlaywrightFetcher
from app.services.extractor import ExtractorService
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.source import Source

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_urls():
    urls = [
        "https://www.mtn.co.za/home/mobile/plans",
        "https://ee.co.uk/pay-monthly",
        "https://www.econet.co.zw/voice/"
    ]
    
    db = SessionLocal()
    fetcher = PlaywrightFetcher()
    extractor_service = ExtractorService(db)
    
    print("\n" + "="*80)
    print(f"{'URL':<50} | {'Records':<10} | {'Status'}")
    print("-" * 80)
    
    for url in urls:
        try:
            # Fetch
            content = await fetcher.fetch_page_content(url)
            
            # Create a temporary snapshot (not saved to DB for test, or saved then deleted)
            snapshot = RawSnapshot(
                url=url,
                content=content,
                content_type="html"
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            
            # Extract
            records = extractor_service.extract_from_snapshot(snapshot)
            
            status = "SUCCESS" if len(records) > 0 else "FAILED"
            print(f"{url[:50]:<50} | {len(records):<10} | {status}")
            
            if len(records) > 0:
                print(f"   Sample: {records[0]['title']} - {records[0]['price_currency']}{records[0]['price_value']}")
            
        except Exception as e:
            print(f"{url[:50]:<50} | ERROR      | {e}")
            
    print("="*80 + "\n")
    db.close()

if __name__ == "__main__":
    asyncio.run(test_urls())
