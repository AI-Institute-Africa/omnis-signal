import logging
from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.scraping.org_pipeline import OrgScrapePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_econet():
    db = SessionLocal()
    org = db.query(Organization).filter(Organization.id == 43).first()
    
    if not org:
        print("Econet (ID 43) not found in DB.")
        return

    print(f"--- Starting Scrape for {org.name} ---")
    pipeline = OrgScrapePipeline(db)
    pipeline.run(org)
    
    # Refresh org data
    db.refresh(org)
    
    print("\n--- Scrape Results ---")
    print(f"AI Summary: {org.ai_summary}")
    print(f"Risk Score: {org.risk_score}")
    print(f"Reputation Score: {org.reputation_score}")
    print(f"Data Completeness: {org.data_completeness}%")
    
    # Check catalog
    from app.db.models.product import Product
    from app.db.models.service import Service
    
    products = db.query(Product).filter(Product.organization_id == org.id).all()
    services = db.query(Service).filter(Service.organization_id == org.id).all()
    
    print(f"\nExtracted Products ({len(products)}):")
    for p in products:
        print(f"- {p.name} ({p.category})")
        
    print(f"\nExtracted Services ({len(services)}):")
    for s in services:
        print(f"- {s.name} ({s.category})")

    db.close()

if __name__ == "__main__":
    test_econet()
