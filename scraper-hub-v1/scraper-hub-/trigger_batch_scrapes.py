import logging
from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.scraping.org_pipeline import OrgScrapePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_batch(limit=5):
    db = SessionLocal()
    # Find organizations that haven't been scraped yet
    orgs = db.query(Organization).filter(Organization.ai_summary == None).limit(limit).all()
    
    if not orgs:
        print("No pending organizations found.")
        return

    print(f"--- Starting Batch Scrape for {len(orgs)} organizations ---")
    pipeline = OrgScrapePipeline(db)
    
    for i, org in enumerate(orgs):
        print(f"[{i+1}/{len(orgs)}] Processing: {org.name} ({org.website})")
        try:
            pipeline.run(org)
            print(f"  SUCCESS: {org.name}")
        except Exception as e:
            print(f"  FAILED: {org.name} - {e}")

    db.close()

if __name__ == "__main__":
    run_batch(5) # Small batch to avoid long wait
