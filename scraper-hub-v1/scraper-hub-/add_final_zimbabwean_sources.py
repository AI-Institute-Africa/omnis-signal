from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

def add_comprehensive_zim_sources():
    db = SessionLocal()
    
    # 1. More Zimbabwean Banks
    banks = [
        {"name": "CABS Zimbabwe", "url": "https://www.cabs.co.zw/banking/personal-banking/accounts"},
        {"name": "Nedbank Zimbabwe", "url": "https://www.nedbank.co.zw/personal/banking/accounts"},
        {"name": "First Capital Bank ZW", "url": "https://firstcapitalbank.co.zw/personal/banking/accounts"},
        {"name": "Steward Bank", "url": "https://www.stewardbank.co.zw/personal-banking/accounts"},
        {"name": "FBC Bank", "url": "https://www.fbc.co.zw/bank/personal/banking/accounts"},
        {"name": "NMB Bank Zimbabwe", "url": "https://nmbz.co.zw/personal/banking/accounts"},
        {"name": "BancABC Zimbabwe", "url": "https://www.bancabc.co.zw/personal/banking/accounts"}
    ]
    
    # 2. More Zimbabwean Telecoms
    telecoms = [
        {"name": "NetOne Zimbabwe", "url": "https://www.netone.co.zw/personal/data-bundles"},
        {"name": "Telecel Zimbabwe", "url": "https://www.telecel.co.zw/personal/data-bundles"}
    ]
    
    # 3. Major High and Primary Schools in Zimbabwe
    schools = [
        {"name": "Arundel School", "url": "https://arundel.ac.zw/admissions/fees/"},
        {"name": "Chisipite Senior School", "url": "https://chisipite.com/admissions/fees/"},
        {"name": "St George's College", "url": "https://stgeorges.co.zw/admissions/fees/"},
        {"name": "Peterhouse Group of Schools", "url": "https://www.peterhousegroup.co.zw/admissions/fees/"},
        {"name": "Gateway Schools", "url": "https://gateway.ac.zw/admissions/fees/"},
        {"name": "Hellenic Academy", "url": "https://hellenicacademy.com/admissions/fees/"},
        {"name": "Lomagundi College", "url": "https://lomagundi.com/admissions/fees/"},
        {"name": "Falcon College", "url": "https://falconcollege.com/admissions/fees/"}
    ]

    for bank in banks:
        s = Source(name=bank["name"], category="banking", base_url=bank["url"])
        db.add(s)
        db.commit()
        db.refresh(s)
        p = SourcePage(source_id=s.id, url=bank["url"], page_type="accounts")
        db.add(p)
    
    for telecom in telecoms:
        s = Source(name=telecom["name"], category="telecom", base_url=telecom["url"])
        db.add(s)
        db.commit()
        db.refresh(s)
        p = SourcePage(source_id=s.id, url=telecom["url"], page_type="data_bundles")
        db.add(p)

    for school in schools:
        s = Source(name=school["name"], category="schools", base_url=school["url"])
        db.add(s)
        db.commit()
        db.refresh(s)
        p = SourcePage(source_id=s.id, url=school["url"], page_type="fees")
        db.add(p)

    db.commit()
    db.close()
    print("Added comprehensive Zimbabwean banks, telecoms, and schools.")

if __name__ == "__main__":
    add_comprehensive_zim_sources()
