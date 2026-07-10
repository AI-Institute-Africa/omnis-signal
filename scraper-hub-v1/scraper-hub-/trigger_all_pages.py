import asyncio
from app.db.session import SessionLocal
from app.db.models.source_page import SourcePage
from app.jobs.tasks import scrape_source

async def trigger_all_pages():
    db = SessionLocal()
    pages = db.query(SourcePage).all()
    print(f"Found {len(pages)} pages.")
    
    count = 0
    for page in pages:
        print(f"Triggering {page.url}")
        try:
            await scrape_source(page.id)
            count += 1
        except Exception as e:
            print(f"Failed {page.url}: {e}")
            
    print(f"Successfully triggered {count} pages.")
    db.close()

if __name__ == "__main__":
    asyncio.run(trigger_all_pages())
