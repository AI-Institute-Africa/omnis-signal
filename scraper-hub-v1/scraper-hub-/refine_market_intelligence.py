import logging
from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.db.models.product import Product
from app.db.models.service import Service
from app.db.models.price_entry import PriceEntry
from app.scraping.org_pipeline import OrgScrapePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TARGET_SECTORS = ["telecoms", "telecom", "internet", "universities", "colleges", "hospitals", "medical", "hotels", "tourism"]

def refine_intelligence():
    db = SessionLocal()
    
    # 1. Find organizations in target sectors
    orgs = db.query(Organization).filter(
        Organization.category.in_(TARGET_SECTORS)
    ).all()
    
    print(f"Found {len(orgs)} organizations in target sectors.")
    
    # 2. Purge old data for these organizations to ensure "Real Prices" only
    org_ids = [o.id for o in orgs]
    if org_ids:
        print("Purging old products and services for target sectors...")
        db.query(PriceEntry).filter(PriceEntry.organization_id.in_(org_ids)).delete(synchronize_session=False)
        db.query(Product).filter(Product.organization_id.in_(org_ids)).delete(synchronize_session=False)
        db.query(Service).filter(Service.organization_id.in_(org_ids)).delete(synchronize_session=False)
        db.commit()

    # 3. Trigger new scrapes
    pipeline = OrgScrapePipeline(db)
    for i, org in enumerate(orgs):
        print(f"[{i+1}/{len(orgs)}] Refining Intelligence for: {org.name} ({org.category})")
        try:
            # We use the pipeline which now uses the updated OrgIntelligenceService
            pipeline.run(org)
            print(f"  SUCCESS: {org.name}")
        except Exception as e:
            print(f"  FAILED: {org.name} - {e}")
            
    db.close()
    print("Market Intelligence Refinement Complete.")

if __name__ == "__main__":
    refine_intelligence()
