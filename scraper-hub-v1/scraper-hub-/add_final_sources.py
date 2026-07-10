from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

def add_sources():
    db = SessionLocal()
    
    # 1. Hospitality: Cresta Hotels
    cresta = db.query(Source).filter(Source.name == "Cresta Hotels").first()
    if not cresta:
        cresta = Source(name="Cresta Hotels", category="hotels", base_url="https://www.crestahotels.com/")
        db.add(cresta)
        db.commit()
        db.refresh(cresta)
    
    cresta_pages = [
        "https://www.crestahotels.com/hotels/cresta-lodge-harare",
        "https://www.crestahotels.com/hotels/cresta-oasis",
        "https://www.crestahotels.com/hotels/cresta-churchill"
    ]
    for url in cresta_pages:
        if not db.query(SourcePage).filter(SourcePage.url == url).first():
            db.add(SourcePage(source_id=cresta.id, url=url, page_type="product", enabled=True))

    # 2. Utilities: City of Harare (Rates and Water)
    harare = db.query(Source).filter(Source.name == "City of Harare").first()
    if not harare:
        harare = Source(name="City of Harare", category="utilities", base_url="https://www.hararecity.co.zw/")
        db.add(harare)
        db.commit()
        db.refresh(harare)
        
    harare_pages = [
        "https://www.hararecity.co.zw/rates-tariffs/",
        "https://www.hararecity.co.zw/water-charges/"
    ]
    for url in harare_pages:
        if not db.query(SourcePage).filter(SourcePage.url == url).first():
            db.add(SourcePage(source_id=harare.id, url=url, page_type="product", enabled=True))

    # 3. Energy: ZERA (Zimbabwe Energy Regulatory Authority) - Fuel and Electricity
    zera = db.query(Source).filter(Source.name == "ZERA").first()
    if not zera:
        zera = Source(name="ZERA", category="utilities", base_url="https://www.zera.co.zw/")
        db.add(zera)
        db.commit()
        db.refresh(zera)
        
    zera_pages = [
        "https://www.zera.co.zw/fuel-prices/",
        "https://www.zera.co.zw/electricity-tariffs/"
    ]
    for url in zera_pages:
        if not db.query(SourcePage).filter(SourcePage.url == url).first():
            db.add(SourcePage(source_id=zera.id, url=url, page_type="product", enabled=True))

    db.commit()
    print("Final sources added successfully.")
    db.close()

if __name__ == "__main__":
    add_sources()
