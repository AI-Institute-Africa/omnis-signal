from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

def generate_missing_pages():
    db = SessionLocal()
    sources = db.query(Source).all()
    
    added_count = 0
    for source in sources:
        # Check if source has any pages
        has_pages = db.query(SourcePage).filter(SourcePage.source_id == source.id).first()
        if not has_pages:
            new_page = SourcePage(
                source_id=source.id,
                url=source.base_url,
                page_type='general',
                enabled=True
            )
            db.add(new_page)
            added_count += 1
            print(f"Generated default page for {source.name} ({source.base_url})")
            
    db.commit()
    db.close()
    print(f"Total default pages generated: {added_count}")

if __name__ == "__main__":
    generate_missing_pages()
