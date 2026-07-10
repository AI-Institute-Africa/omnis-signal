# Scraper Hub

Scraper Hub is a Python-based scraping platform that uses Playwright, PostgreSQL, and background workers to collect, normalize, store, review, and distribute pricing/product/tariff data from configured web sources.

## Stack
- Python
- FastAPI
- Playwright
- PostgreSQL
- Alembic
- Redis + RQ
- APScheduler
- Jinja2/HTMX for admin UI

## Main capabilities
- Scheduled source scraping
- Manual URL scraping
- Source-specific extractors and fallback parsing
- Raw snapshot storage
- Normalized records for browsing and search
- Outbound webhook/API publishing to downstream systems
- Web UI for dashboard, sources, manual scrape, records
- Background job queue with retries and alerts

## Local setup
1. Copy `.env.example` to `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `alembic upgrade head`
4. Start API: `uvicorn app.main:app --reload`
5. Start RQ worker: `rq worker`
6. (Optional) Start scheduler: integrated in app startup

## Environment variables
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection for queues
- `PLAYWRIGHT_HEADLESS`: Run browser headless (default: true)
- `WEBHOOK_SIGNING_SECRET`: Secret for signing outbound webhooks

## How to add a new source
1. Create a source via API: `POST /api/v1/sources`
2. Add pages: Include in the source creation or update
3. Implement extractor if needed in `app/scraping/extractors/`
4. Test with manual scrape

## How manual scraping works
- `POST /api/v1/scrape` with URL
- Returns raw content and extracted records

## Web UI
- Dashboard: Overview of sources, records, snapshots
- Sources: List and manage sources, trigger scrapes
- Manual Scrape: Scrape a single URL
- Records: Browse extracted records

## How outbound integrations work
- Configure webhook targets: `POST /api/v1/webhook-targets/`
- View delivery attempts: `GET /api/v1/delivery-attempts/`
- Replay failed deliveries: `POST /api/v1/webhook-targets/{target_id}/replay-failed`
- Records trigger events sent to configured URLs with HMAC signature
- Failed webhook deliveries are tracked and moved to a dead-letter queue for replay
