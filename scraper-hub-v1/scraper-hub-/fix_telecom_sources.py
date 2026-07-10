from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

def fix_telecom():
    db = SessionLocal()
    
    # 1. Delete all existing Zimbabwean telecom sources to start fresh and avoid duplicates/404s
    # We'll keep Econet since it's working well, but replace others
    telecom_sources = db.query(Source).filter(Source.category == 'telecom', Source.market == 'local').all()
    for s in telecom_sources:
        if 'Econet' not in s.name:
            print(f"Deleting old/incorrect source: {s.name} (ID: {s.id})")
            # Delete associated pages first
            db.query(SourcePage).filter(SourcePage.source_id == s.id).delete()
            db.delete(s)
    
    db.commit()

    # 2. Add correct, verified telecom sources
    NEW_SOURCES = [
        {
            "name": "Telecel USD Bundles",
            "category": "telecom",
            "market": "local",
            "base_url": "https://telecel.co.zw/usd-data-service/"
        },
        {
            "name": "Telecel ZiG Bundles",
            "category": "telecom",
            "market": "local",
            "base_url": "https://telecel.co.zw/zig-data-service/"
        },
        {
            "name": "TelOne Tariffs",
            "category": "telecom",
            "market": "local",
            "base_url": "https://www.telone.co.zw/products/details/service-tariffs-effective-5-august-2025"
        },
        {
            "name": "Liquid Home FibroniX",
            "category": "telecom",
            "market": "local",
            "base_url": "https://zw.liquidhome.tech/get-connected/fibronix"
        },
        {
            "name": "Liquid Home WibroniX",
            "category": "telecom",
            "market": "local",
            "base_url": "https://zw.liquidhome.tech/get-connected/wibronix"
        },
        {
            "name": "NetOne Data Bundles",
            "category": "telecom",
            "market": "local",
            "base_url": "https://www.netone.co.zw/data-bundles/"
        },
        {
            "name": "PowerTel Promotions",
            "category": "telecom",
            "market": "local",
            "base_url": "https://www.powertel.co.zw/"
        },
        {
            "name": "Africom Data Services",
            "category": "telecom",
            "market": "local",
            "base_url": "https://africom.co.zw/product-category/data-services/"
        },
        {
            "name": "Utande Home Fibre",
            "category": "telecom",
            "market": "local",
            "base_url": "https://www.dandemutande.co.zw/home-fibre/"
        }
    ]

    for src_data in NEW_SOURCES:
        new_src = Source(**src_data)
        db.add(new_src)
        db.flush() # Get ID
        
        # Add a page for it
        new_page = SourcePage(
            source_id=new_src.id,
            url=new_src.base_url,
            page_type='general',
            enabled=True
        )
        db.add(new_page)
        print(f"Added fresh source: {new_src.name}")

    db.commit()
    db.close()
    print("Telecom source fix complete.")

if __name__ == "__main__":
    fix_telecom()
