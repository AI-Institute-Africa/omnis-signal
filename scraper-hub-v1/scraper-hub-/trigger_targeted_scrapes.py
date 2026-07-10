import asyncio
from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage
from app.jobs.tasks import scrape_source
from datetime import datetime, timedelta


def trigger_targeted_scrapes():
    db = SessionLocal()
    
    # Trigger scrapes for pages added in the last 10 minutes
    one_hour_ago = datetime.utcnow() - timedelta(minutes=10)

    new_pages = db.query(SourcePage).filter(SourcePage.created_at >= one_hour_ago).all()
    
    # Get unique source IDs to avoid redundant scraping of the same source
    source_ids = sorted(list(set(page.source_id for page in new_pages)))
    
    print(f"Found {len(new_pages)} recently added pages across {len(source_ids)} sources.")
    
    count = 0
    for sid in source_ids:
        source = db.query(Source).filter(Source.id == sid).first()
        if not source: continue
        
        print(f"[{count+1}/{len(source_ids)}] Triggering scrape for source: {source.name} (ID: {sid})")
        try:
            # scrape_source is a sync function that handles its own loop
            scrape_source(sid)
            count += 1
            print(f"  SUCCESS")
        except Exception as e:
            print(f"  FAILED: {e}")
            
    print(f"\nTargeted scraping complete. Successfully processed {count} sources.")
    db.close()

if __name__ == "__main__":
    # The script itself doesn't need to be async if we are just calling scrape_source
    trigger_targeted_scrapes()

