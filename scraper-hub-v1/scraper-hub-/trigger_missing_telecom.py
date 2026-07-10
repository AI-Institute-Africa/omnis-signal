from app.db.session import SessionLocal
from app.db.models.source import Source
from app.jobs.tasks import scrape_source

def trigger_telecom():
    db = SessionLocal()
    # Explicitly target missing or under-represented telecom IDs
    telecom_ids = [174, 175, 191, 192, 193, 194, 195, 196, 198, 199, 200]
    
    sources = db.query(Source).filter(Source.id.in_(telecom_ids)).all()
    
    print(f"Targeting {len(sources)} specific telecom sources...")
    
    for i, source in enumerate(sources):
        print(f"[{i+1}/{len(sources)}] SCRAPING: {source.name} ({source.base_url})")
        try:
            scrape_source(source.id)
            print(f"  DONE: {source.name}")
        except Exception as e:
            print(f"  FAILED: {e}")
            
    db.close()
    print("Finished missing telecom scrape.")

if __name__ == "__main__":
    trigger_telecom()
