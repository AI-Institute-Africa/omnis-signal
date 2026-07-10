import logging
from app.db.session import SessionLocal
from app.db.models.source import Source
from app.jobs.tasks import scrape_source

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trigger_all")

def trigger_all():
    db = SessionLocal()
    try:
        # Get all sources
        sources = db.query(Source).all()
        print(f"Total sources found: {len(sources)}")
        
        # Categorize for reporting
        by_cat = {}
        for s in sources:
            by_cat[s.category] = by_cat.get(s.category, 0) + 1
        
        print("Source distribution by category:")
        for cat, count in by_cat.items():
            print(f"  - {cat}: {count}")

        triggered_count = 0
        for source in sources:
            if not source.pages:
                continue
                
            print(f"Triggering {source.name} [{source.category}] - {len(source.pages)} pages")
            try:
                # We call scrape_source which handles fetching and AI extraction
                scrape_source(source.id)
                triggered_count += 1
            except Exception as e:
                print(f"Error scraping {source.name}: {e}")

        print(f"Finished. Total sources triggered: {triggered_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    trigger_all()
