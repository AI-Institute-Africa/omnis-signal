import os
import sys

sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage
from app.db.models.raw_snapshot import RawSnapshot
from app.services.fetcher import PlaywrightFetcher
from app.services.extractor import ExtractorService

TELECEL_URL = "https://www.telecel.co.zw/value-added-services/"
SOURCE_NAME = "Telecel Value Added Services"


def ensure_telecel_source(db):
    source = db.query(Source).filter(Source.base_url == TELECEL_URL).first()
    if not source:
        source = db.query(Source).filter(Source.name == SOURCE_NAME).first()
    if not source:
        source = Source(
            name=SOURCE_NAME,
            category="telecom",
            market="local",
            base_url=TELECEL_URL,
            schedule="0 9 * * *"
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        print(f"Created source id={source.id} for {TELECEL_URL}")
    else:
        print(f"Found existing source id={source.id} for {TELECEL_URL}")

    page = db.query(SourcePage).filter(SourcePage.url == TELECEL_URL, SourcePage.source_id == source.id).first()
    if not page:
        page = SourcePage(
            source_id=source.id,
            url=TELECEL_URL,
            page_type="value_added_services",
            enabled=True,
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        print(f"Created source page id={page.id} for source id={source.id}")
    else:
        print(f"Found existing source page id={page.id} for source id={source.id}")

    return source, page


def scrape_telecel_page(db, page):
    fetcher = PlaywrightFetcher()
    extractor = ExtractorService(db)
    
    print(f"Fetching page {page.url}")
    content = None
    try:
        import asyncio
        content = asyncio.run(fetcher.fetch_page_content(page.url))
    except Exception as e:
        print(f"Fetch failed: {type(e).__name__}: {e}")
        raise

    if not content:
        raise RuntimeError("Fetcher returned empty content")

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
        print(f"{idx}. {rec.get('title', 'N/A')} - {rec.get('price_value')} {rec.get('price_currency', '')}")
    return records


if __name__ == "__main__":
    db = SessionLocal()
    try:
        source, page = ensure_telecel_source(db)
        records = scrape_telecel_page(db, page)
        print("Done.")
    finally:
        db.close()
