from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage
from app.db.models.raw_snapshot import RawSnapshot
from app.services.fetcher import PlaywrightFetcher
from app.services.extractor import ExtractorService

UNIVERSITIES = [
    {
        "name": "University of Zimbabwe",
        "base_url": "https://www.uz.ac.zw/",
        "pages": [
            {"url": "https://www.uz.ac.zw/index.php/study-at-uz/undergraduates", "page_type": "education"},
            {"url": "https://www.uz.ac.zw/index.php/current-students/undergraduates/fees", "page_type": "fees"}
        ]
    },
    {
        "name": "National University of Science and Technology",
        "base_url": "https://www.nust.ac.zw/",
        "pages": [
            {"url": "https://www.nust.ac.zw/", "page_type": "education"},
            {"url": "https://www.nust.ac.zw/", "page_type": "fees"}
        ]
    },
    {
        "name": "Midlands State University",
        "base_url": "https://www.msu.ac.zw/",
        "pages": [
            {"url": "https://www.msu.ac.zw/", "page_type": "education"},
            {"url": "https://www.msu.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Chinhoyi University of Technology",
        "base_url": "https://www.cut.ac.zw/",
        "pages": [
            {"url": "https://www.cut.ac.zw/", "page_type": "education"},
            {"url": "https://www.cut.ac.zw/fees-structure/", "page_type": "fees"}
        ]
    },
    {
        "name": "Bindura University of Science Education",
        "base_url": "https://www.buse.ac.zw/",
        "pages": [
            {"url": "https://www.buse.ac.zw/", "page_type": "education"},
            {"url": "https://www.buse.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Great Zimbabwe University",
        "base_url": "https://www.gzu.ac.zw/",
        "pages": [
            {"url": "https://www.gzu.ac.zw/", "page_type": "education"},
            {"url": "https://www.gzu.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Harare Institute of Technology",
        "base_url": "https://www.hit.ac.zw/",
        "pages": [
            {"url": "https://www.hit.ac.zw/", "page_type": "education"},
            {"url": "https://www.hit.ac.zw/student-fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Zimbabwe Open University",
        "base_url": "https://www.zou.ac.zw/",
        "pages": [
            {"url": "https://www.zou.ac.zw/", "page_type": "education"},
            {"url": "https://www.zou.ac.zw/", "page_type": "fees"}
        ]
    },
    {
        "name": "Lupane State University",
        "base_url": "https://www.lsu.ac.zw/",
        "pages": [
            {"url": "https://www.lsu.ac.zw/", "page_type": "education"},
            {"url": "https://www.lsu.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Gwanda State University",
        "base_url": "https://www.gsu.ac.zw/",
        "pages": [
            {"url": "https://www.gsu.ac.zw/", "page_type": "education"},
            {"url": "https://www.gsu.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Africa University",
        "base_url": "https://www.africau.edu/",
        "pages": [
            {"url": "https://www.africau.edu/", "page_type": "education"},
            {"url": "https://www.africau.edu/", "page_type": "fees"}
        ]
    },
    {
        "name": "Women's University in Africa",
        "base_url": "https://www.wua.ac.zw/",
        "pages": [
            {"url": "https://www.wua.ac.zw/", "page_type": "education"},
            {"url": "https://www.wua.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Catholic University of Zimbabwe",
        "base_url": "https://www.cuz.ac.zw/",
        "pages": [
            {"url": "https://www.cuz.ac.zw/", "page_type": "education"},
            {"url": "https://www.cuz.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Solusi University",
        "base_url": "https://www.solusi.ac.zw/",
        "pages": [
            {"url": "https://www.solusi.ac.zw/", "page_type": "education"},
            {"url": "https://www.solusi.ac.zw/fees/", "page_type": "fees"}
        ]
    },
    {
        "name": "Reformed Church University",
        "base_url": "https://www.rcu.ac.zw/",
        "pages": [
            {"url": "https://www.rcu.ac.zw/", "page_type": "education"},
            {"url": "https://www.rcu.ac.zw/fees/", "page_type": "fees"}
        ]
    }
]


def ensure_university_sources(db):
    results = {
        "sources_added": 0,
        "sources_existing": 0,
        "pages_added": 0,
        "pages_existing": 0,
    }

    for university in UNIVERSITIES:
        source = db.query(Source).filter(Source.base_url == university["base_url"]).first()
        if source:
            results["sources_existing"] += 1
            if source.name != university["name"]:
                source.name = university["name"]
                db.add(source)
        else:
            source = Source(
                name=university["name"],
                category="education",
                market="local",
                base_url=university["base_url"],
                schedule="0 8 * * *"
            )
            db.add(source)
            db.flush()
            results["sources_added"] += 1

        for page in university["pages"]:
            existing_page = db.query(SourcePage).filter(
                SourcePage.source_id == source.id,
                SourcePage.url == page["url"]
            ).first()
            if existing_page:
                results["pages_existing"] += 1
            else:
                new_page = SourcePage(
                    source_id=source.id,
                    url=page["url"],
                    page_type=page["page_type"],
                    enabled=True,
                    schedule="0 8 * * *"
                )
                db.add(new_page)
                results["pages_added"] += 1

    db.commit()
    return results


def scrape_pages(db):
    fetcher = PlaywrightFetcher()
    extractor = ExtractorService(db)
    page_count = 0
    record_count = 0

    pages = db.query(SourcePage).join(SourcePage.source).filter(
        SourcePage.enabled == True,
        Source.category == "education",
        Source.base_url.in_([u["base_url"] for u in UNIVERSITIES])
    ).all()

    for page in pages:
        page_count += 1
        print(f"\n=== Scraping {page.source.name} page: {page.url} ===")
        try:
            import asyncio
            content = asyncio.run(fetcher.fetch_page_content(page.url))
        except Exception as exc:
            print(f"Failed to fetch {page.url}: {type(exc).__name__}: {exc}")
            continue

        if not content:
            print(f"No content returned for {page.url}")
            continue

        snapshot = RawSnapshot(
            source_page_id=page.id,
            url=page.url,
            content=content,
            content_type="html"
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        try:
            records = extractor.extract_from_snapshot(
                snapshot,
                category_hint="education",
                extractor_type="auto",
                persist=True,
                run_ai_enrichment=False,
                real_prices_only=True,
            )
        except Exception as exc:
            print(f"Extraction failed for {page.url}: {type(exc).__name__}: {exc}")
            continue

        record_count += len(records)
        print(f"Extracted {len(records)} records from {page.url}")

    print(f"\nScraped {page_count} education pages and extracted {record_count} price records.")
    return page_count, record_count


def main():
    db = SessionLocal()
    try:
        summary = ensure_university_sources(db)
        print("Source registration summary:")
        print(summary)
        page_count, record_count = scrape_pages(db)
        print(f"Finished scraping {page_count} pages. Total records extracted: {record_count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
