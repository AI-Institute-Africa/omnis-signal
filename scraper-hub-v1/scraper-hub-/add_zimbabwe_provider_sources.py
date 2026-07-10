import os
import sys

sys.path.append(os.getcwd())

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

PROVIDERS = [
    {
        "name": "TelOne",
        "category": "telecom",
        "market": "local",
        "base_url": "https://www.telone.co.zw/Products/Broadband",
        "pages": [
            {"url": "https://www.telone.co.zw/Products/Broadband", "page_type": "general"},
            {"url": "https://www.telone.co.zw/products/details/service-tariffs-effective-5-august-2025", "page_type": "general"}
        ]
    },
    {
        "name": "Africom",
        "category": "telecom",
        "market": "local",
        "base_url": "https://africom.co.zw/product-category/data-services/",
        "pages": [
            {"url": "https://africom.co.zw/product-category/data-services/", "page_type": "general"}
        ]
    },
    {
        "name": "Liquid Home Zimbabwe",
        "category": "telecom",
        "market": "local",
        "base_url": "https://www.liquidhome.co.zw/packages/",
        "pages": [
            {"url": "https://www.liquidhome.co.zw/packages/", "page_type": "general"}
        ]
    },
    {
        "name": "Dandemutande",
        "category": "telecom",
        "market": "local",
        "base_url": "https://www.dandemutande.co.zw/home-fibre/",
        "pages": [
            {"url": "https://www.dandemutande.co.zw/home-fibre/", "page_type": "general"}
        ]
    },
    {
        "name": "Utande Internet Services",
        "category": "telecom",
        "market": "local",
        "base_url": "https://www.utande.co.zw/",
        "pages": [
            {"url": "https://www.utande.co.zw/", "page_type": "general"}
        ]
    },
    {
        "name": "Tagtel",
        "category": "telecom",
        "market": "local",
        "base_url": "https://www.tagtel.co.zw/data-plans/",
        "pages": [
            {"url": "https://www.tagtel.co.zw/data-plans/", "page_type": "general"}
        ]
    },
    {
        "name": "ZOL Zimbabwe",
        "category": "telecom",
        "market": "local",
        "base_url": "https://www.zol.co.zw/",
        "pages": [
            {"url": "https://www.zol.co.zw/", "page_type": "general"}
        ]
    }
]


def add_provider_sources():
    db: Session = SessionLocal()
    summary = {
        "sources_added": 0,
        "sources_existing": 0,
        "pages_added": 0,
        "pages_existing": 0,
    }

    try:
        for provider in PROVIDERS:
            source = db.query(Source).filter(Source.base_url == provider["base_url"]).first()
            if source:
                if source.name != provider["name"]:
                    print(f"Updating source name: {source.name} -> {provider['name']} for {source.base_url}")
                    source.name = provider["name"]
                summary["sources_existing"] += 1
                print(f"Source already exists: {source.name} -> {source.base_url}")
            else:
                source = Source(
                    name=provider["name"],
                    category=provider["category"],
                    market=provider["market"],
                    base_url=provider["base_url"],
                    schedule="0 7 * * *"
                )
                db.add(source)
                db.flush()
                summary["sources_added"] += 1
                print(f"Added source: {source.name} -> {source.base_url}")

            for page in provider["pages"]:
                existing_page = db.query(SourcePage).filter(SourcePage.url == page["url"]).first()
                if existing_page:
                    summary["pages_existing"] += 1
                    print(f"Page already exists: {existing_page.url}")
                else:
                    new_page = SourcePage(
                        source_id=source.id,
                        url=page["url"],
                        page_type=page["page_type"],
                        enabled=True,
                        schedule="0 7 * * *"
                    )
                    db.add(new_page)
                    summary["pages_added"] += 1
                    print(f"Added page: {new_page.url}")

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error while adding provider sources: {e}")
    finally:
        db.close()

    print("\n=== Summary ===")
    print(f"Sources added: {summary['sources_added']}")
    print(f"Sources already existing: {summary['sources_existing']}")
    print(f"Pages added: {summary['pages_added']}")
    print(f"Pages already existing: {summary['pages_existing']}")


if __name__ == "__main__":
    add_provider_sources()
