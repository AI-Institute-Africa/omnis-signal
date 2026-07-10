from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

def refine_sources():
    db = SessionLocal()
    
    # Mapping of Source Name to list of specific product URLs
    TARGET_PAGES = {
        # TELECOM
        'Econet Wireless': [
            'https://www.econet.co.zw/usd-data-bundles/',
            'https://www.econet.co.zw/voice/',
            'https://www.econet.co.zw/5g/',
        ],
        'NetOne Zimbabwe': [
            'https://www.netone.co.zw/data-bundles/',
            'https://www.netone.co.zw/voice-tariffs/',
            'https://www.netone.co.zw/onefi-bundles/',
        ],
        'Telecel Zimbabwe': [
            'https://www.telecel.co.zw/data-plans/',
            'https://www.telecel.co.zw/voice-plans/',
        ],
        
        # BANKING
        'CBZ Bank': [
            'https://www.cbz.co.zw/personal-banking/accounts/current-account/',
            'https://www.cbz.co.zw/personal-banking/loans/personal-loans/',
            'https://www.cbz.co.zw/personal-banking/mortgages/',
        ],
        'FBC Bank': [
            'https://www.fbc.co.zw/personal/banking/accounts',
            'https://www.fbc.co.zw/personal/banking/loans',
        ],
        'Stanbic Bank Zimbabwe': [
            'https://www.stanbicbank.co.zw/zimbabwe/personal/products-and-services/bank-with-us/current-accounts',
            'https://www.stanbicbank.co.zw/zimbabwe/personal/products-and-services/borrow-for-your-needs',
        ],
        
        # EDUCATION
        'University of Zimbabwe': [
            'https://www.uz.ac.zw/fees/',
            'https://www.uz.ac.zw/undergraduate-admissions/',
        ],
        'NUST Zimbabwe': [
            'https://www.nust.ac.zw/index.php/admissions/fees.html',
            'https://www.nust.ac.zw/index.php/admissions/undergraduate.html',
        ],
        
        # INSURANCE
        'Old Mutual Zimbabwe': [
            'https://www.oldmutual.co.zw/personal/insurance/funeral-plan/',
            'https://www.oldmutual.co.zw/personal/insurance/motor-insurance/',
        ],
        'Zimnat Insurance': [
            'https://zimnat.co.zw/individual-life/',
            'https://zimnat.co.zw/general-insurance/',
        ],
        
        # HOTELS
        'Meikles Hotel': [
            'https://www.meikles.com/rooms-and-suites/',
        ],
        'Rainbow Towers Hotel': [
            'https://rtg.co.zw/rainbow-towers-hotel-conference-centre/accommodation/',
        ],
        
        # ENERGY / SOLAR
        'ZERA (Zimbabwe Energy Authority)': [
            'https://www.zera.co.zw/petroleum-prices/',
            'https://www.zera.co.zw/electricity-tariffs/',
        ]
    }
    
    added_count = 0
    for source_name, urls in TARGET_PAGES.items():
        source = db.query(Source).filter(Source.name == source_name).first()
        if not source:
            print(f"Source NOT FOUND: {source_name}")
            continue
            
        print(f"Processing source: {source_name} (ID: {source.id})")
        for url in urls:
            # Check if this page already exists for this source
            existing = db.query(SourcePage).filter(
                SourcePage.source_id == source.id,
                SourcePage.url == url
            ).first()
            
            if not existing:
                new_page = SourcePage(
                    source_id=source.id,
                    url=url,
                    page_type='product_list',
                    enabled=True
                )
                db.add(new_page)
                added_count += 1
                print(f"  + Added: {url}")
            else:
                print(f"  . Exists: {url}")
                
    db.commit()
    db.close()
    print(f"\nRefinement complete. Added {added_count} new product pages.")

if __name__ == "__main__":
    refine_sources()
