from app.db.session import SessionLocal
from app.db.models import Organization, Source, SourcePage
from urllib.parse import urljoin

def sync():
    db = SessionLocal()
    try:
        orgs = db.query(Organization).filter(Organization.website.isnot(None)).all()
        print(f"Checking {len(orgs)} organizations with websites...")
        
        sources_added = 0
        pages_added = 0
        
        for org in orgs:
            website = org.website.strip()
            if not website.startswith('http'):
                website = 'https://' + website
                
            # Check if source exists
            existing_source = db.query(Source).filter(Source.base_url.contains(org.website)).first()
            
            if not existing_source:
                print(f"Creating source for {org.name}...")
                new_source = Source(
                    name=org.name,
                    category=org.category,
                    base_url=website,
                    schedule="0 0 * * *" # Daily at midnight
                )
                db.add(new_source)
                db.flush() # Get ID
                sources_added += 1
                
                # Add standard pages
                standard_paths = [
                    "", # Home
                    "/pricing",
                    "/products",
                    "/services",
                    "/personal/tariffs",
                    "/business/tariffs",
                    "/rates"
                ]
                
                for path in standard_paths:
                    page_url = urljoin(website, path)
                    new_page = SourcePage(
                        source_id=new_source.id,
                        url=page_url,
                        page_type='products_services' if path != "" else 'general',
                        enabled=True
                    )
                    db.add(new_page)
                    pages_added += 1
            else:
                # Source exists, check if it has pages
                has_pages = db.query(SourcePage).filter(SourcePage.source_id == existing_source.id).first()
                if not has_pages:
                    new_page = SourcePage(
                        source_id=existing_source.id,
                        url=existing_source.base_url,
                        page_type='general',
                        enabled=True
                    )
                    db.add(new_page)
                    pages_added += 1

        db.commit()
        print(f"Sync complete. Added {sources_added} sources and {pages_added} pages.")
        
    finally:
        db.close()

if __name__ == "__main__":
    sync()
