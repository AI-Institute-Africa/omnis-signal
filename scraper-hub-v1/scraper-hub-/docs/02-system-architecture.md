# System Architecture

## Main components
- API service: FastAPI for admin endpoints, data endpoints, UI views
- Worker service: executes scrape and parse jobs
- Scheduler: enqueues recurring source scrapes
- PostgreSQL: stores source configs, raw snapshots, records, events, audit logs
- Redis: queue broker and cache
- Playwright runtime: headless browser for JS-heavy websites
- Extractors: category-specific parsers (telecom, banking, etc.) that normalize raw content into structured records

## Flow
1. Scheduler selects due source pages.
2. Worker opens page using Playwright or fallback fetcher.
3. HTML/PDF/raw content snapshot is stored.
4. Extractor (based on source category) parses content into normalized records.
5. Records are stored in extracted_records table with confidence scores.
6. Outbound event is created for downstream delivery.
7. UI and API expose latest data and history.