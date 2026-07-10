import asyncio
import logging
from app.db.session import SessionLocal
from app.db.models import Organization, Source
from app.jobs.tasks import scrape_source

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trigger_empty_orgs")

def trigger_empty_orgs():
    db = SessionLocal()
    try:
        # Find orgs with no data
        empty_orgs = db.query(Organization).filter(
            ~Organization.products_list.any()
        ).filter(
            ~Organization.services_list.any()
        ).all()
        
        print(f"Found {len(empty_orgs)} organizations with no products/services.")
        
        triggered_count = 0
        for org in empty_orgs:
            # Find the source for this org
            # We match by looking for sources with names similar to the org name 
            # or by base_url containing the website
            source = db.query(Source).filter(
                (Source.name == org.name) | 
                (Source.base_url.contains(org.website if org.website else "NON_EXISTENT_DOMAIN"))
            ).first()
            
            if source and source.pages:
                print(f"Triggering scrape for {org.name} (Source ID: {source.id})")
                try:
                    scrape_source(source.id)
                    triggered_count += 1
                except Exception as e:
                    print(f"Error scraping {org.name}: {e}")
            else:
                print(f"No source/pages found for {org.name}")

        print(f"Finished. Total empty organizations triggered: {triggered_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    trigger_empty_orgs()
