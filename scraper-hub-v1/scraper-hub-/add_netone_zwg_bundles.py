import os
import sys

sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage
from app.db.models.raw_snapshot import RawSnapshot
from app.services.fetcher import PlaywrightFetcher
from app.services.extractor import ExtractorService

NETONE_SOURCE_NAME = "NetOne Data Bundles"
NETONE_ZWG_URL = "https://www.netone.co.zw/zwg-bundles"


def ensure_netone_zwg_page(db):
    source = db.query(Source).filter(Source.name == NETONE_SOURCE_NAME).first()
    if not source:
        print(f"Source '{NETONE_SOURCE_NAME}' not found, creating new NetOne source.")
        source = Source(
            name=NETONE_SOURCE_NAME,
            category="telecom",
            market="local",
            base_url="https://www.netone.co.zw/data-bundles/",
            schedule="0 8 * * *"
        )
        db.add(source)
        db.commit()
        db.refresh(source)
    else:
        print(f"Found existing source id={source.id} for '{NETONE_SOURCE_NAME}'.")

    page = db.query(SourcePage).filter(SourcePage.url == NETONE_ZWG_URL, SourcePage.source_id == source.id).first()
    if not page:
        page = SourcePage(
            source_id=source.id,
            url=NETONE_ZWG_URL,
            page_type="zwg_bundles",
            enabled=True,
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        print(f"Created source page id={page.id} for URL {NETONE_ZWG_URL}")
    else:
        print(f"Found existing source page id={page.id} for URL {NETONE_ZWG_URL}")

    return source, page


def scrape_netone_zwg_page(db, page):
    fetcher = PlaywrightFetcher()
    extractor = ExtractorService(db)
    print(f"Fetching {page.url}")

    import asyncio
    content = asyncio.run(fetcher.fetch_page_content(page.url))
    if not content:
        raise RuntimeError("No content fetched from NetOne ZWG page")

    snapshot = RawSnapshot(
        source_page_id=page.id,
        url=page.url,
        content=content,
        content_type="html"
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    print(f"Saved raw snapshot id={snapshot.id} ({len(content):,} bytes)")

    records = extractor.extract_from_snapshot(
        snapshot,
        category_hint="telecom",
        extractor_type="auto",
        persist=True,
        run_ai_enrichment=False,
        real_prices_only=True,
    )

    print(f"Extraction complete: {len(records)} records persisted")
    for idx, rec in enumerate(records[:20], start=1):
        print(f"{idx}. {rec.get('title', 'N/A')} - {rec.get('price_value')} {rec.get('price_currency')}")
    return records


if __name__ == "__main__":
    db = SessionLocal()
    try:
        source, page = ensure_netone_zwg_page(db)
        scrape_netone_zwg_page(db, page)
    finally:
        db.close()
