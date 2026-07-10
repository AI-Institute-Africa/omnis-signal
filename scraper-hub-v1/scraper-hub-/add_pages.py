from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

def add_pages():
    db = SessionLocal()
    
    # Define pages to add
    pages_to_add = {
        'Stanbic Bank Zimbabwe': [
            'https://www.stanbicbank.co.zw/zimbabwe/personal/products-and-services/bank-with-us/current-accounts',
            'https://www.stanbicbank.co.zw/zimbabwe/personal/products-and-services/borrow-for-your-needs',
        ],
        'HSBC Global': [
            'https://www.hsbc.co.uk/credit-cards/',
            'https://www.hsbc.co.uk/current-accounts/',
        ],
        'MTN Group': [
            'https://www.mtn.co.za/home/mobile/plans',
        ],
        'Vodacom South Africa': [
            'https://www.vodacom.co.za/vodacom/shopping/plans/all-plans',
        ]
    }
    
    added_count = 0
    for source_name, urls in pages_to_add.items():
        source = db.query(Source).filter(Source.name == source_name).first()
        if source:
            for url in urls:
                # Check if page already exists
                existing = db.query(SourcePage).filter(SourcePage.source_id == source.id, SourcePage.url == url).first()
                if not existing:
                    new_page = SourcePage(source_id=source.id, url=url, page_type='product_list', enabled=True)
                    db.add(new_page)
                    added_count += 1
                    print(f"Added page {url} to {source_name}")
                else:
                    print(f"Page {url} already exists for {source_name}")
        else:
            print(f"Source {source_name} not found in DB")
            
    db.commit()
    db.close()
    print(f"Total new pages added: {added_count}")

if __name__ == "__main__":
    add_pages()
