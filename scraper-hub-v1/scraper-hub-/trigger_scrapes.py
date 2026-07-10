import asyncio
from app.db.session import SessionLocal
from app.db.models.source import Source
from app.jobs.tasks import scrape_source

def trigger_now():
    db = SessionLocal()
    # Trigger priority categories first, then the rest
    priority_cats = ['schools', 'universities', 'education', 'utilities', 'solar', 'transport', 'mobility', 'hotels', 'banking', 'telecom']
    
    sources = db.query(Source).all()
    # Sort sources to put priority categories first
    sources.sort(key=lambda s: priority_cats.index(s.category) if s.category in priority_cats else len(priority_cats))
    
    triggered_count = 0
    for source in sources:
        if source.pages:
            print(f"[{source.category}] Triggering Source: {source.name}")
            try:
                scrape_source(source.id)
                triggered_count += 1
            except Exception as e:
                print(f"Error scraping {source.name}: {e}")
    
    print(f"Finished. Total sources triggered: {triggered_count}")
            
    db.close()
    print("Done triggering scrapes.")

if __name__ == "__main__":
    trigger_now()
