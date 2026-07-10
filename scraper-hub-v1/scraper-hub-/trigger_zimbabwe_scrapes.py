import asyncio
from app.db.session import SessionLocal
from app.db.models.source import Source
from app.jobs.tasks import scrape_source

def trigger_zimbabwe():
    db = SessionLocal()
    sources = db.query(Source).filter(Source.market == 'local').all()
    
    print(f"Found {len(sources)} Zimbabwean sources to scrape.")
    
    count = 0
    for source in sources:
        print(f"[{count+1}/{len(sources)}] Triggering: {source.name}")
        try:
            scrape_source(source.id)
            count += 1
        except Exception as e:
            print(f"  Error: {e}")
            
    print(f"Finished. Total Zimbabwean sources scraped: {count}")
    db.close()

if __name__ == "__main__":
    trigger_zimbabwe()
