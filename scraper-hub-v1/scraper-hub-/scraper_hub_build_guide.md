# Scraper Hub Build Guide

## Recommended repository architecture

```text
scraper-hub/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
├── alembic.ini
├── migrations/
│   ├── env.py
│   └── versions/
├── docs/
│   ├── 00-project-overview.md
│   ├── 01-product-requirements.md
│   ├── 02-system-architecture.md
│   ├── 03-source-catalog.md
│   ├── 04-data-model.md
│   ├── 05-scraping-strategy.md
│   ├── 06-parser-rules.md
│   ├── 07-api-contracts.md
│   ├── 08-ui-pages.md
│   ├── 09-job-orchestration.md
│   ├── 10-error-handling-observability.md
│   ├── 11-security-compliance.md
│   ├── 12-testing-strategy.md
│   ├── 13-deployment-runbook.md
│   ├── 14-agent-build-order.md
│   └── 15-definition-of-done.md
├── scripts/
│   ├── bootstrap.sh
│   ├── run_worker.sh
│   ├── run_api.sh
│   ├── seed_sources.py
│   └── backfill_manual_urls.py
├── infra/
│   ├── docker/
│   │   ├── api.Dockerfile
│   │   ├── worker.Dockerfile
│   │   └── scheduler.Dockerfile
│   ├── nginx/
│   │   └── default.conf
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana-dashboards/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── logging.py
│   ├── dependencies.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models/
│   │   │   ├── source.py
│   │   │   ├── source_page.py
│   │   │   ├── scrape_job.py
│   │   │   ├── scrape_run.py
│   │   │   ├── extracted_record.py
│   │   │   ├── extracted_field.py
│   │   │   ├── raw_snapshot.py
│   │   │   ├── outbound_event.py
│   │   │   ├── webhook_target.py
│   │   │   └── audit_log.py
│   │   ├── repositories/
│   │   └── migrations_helpers/
│   ├── schemas/
│   │   ├── source.py
│   │   ├── scrape.py
│   │   ├── record.py
│   │   ├── webhook.py
│   │   └── health.py
│   ├── api/
│   │   ├── router.py
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── sources.py
│   │   │   ├── manual_scrape.py
│   │   │   ├── jobs.py
│   │   │   ├── records.py
│   │   │   ├── exports.py
│   │   │   └── integrations.py
│   ├── services/
│   │   ├── source_service.py
│   │   ├── scrape_service.py
│   │   ├── parse_service.py
│   │   ├── snapshot_service.py
│   │   ├── normalization_service.py
│   │   ├── dedup_service.py
│   │   ├── outbound_service.py
│   │   └── search_service.py
│   ├── workers/
│   │   ├── queue.py
│   │   ├── tasks/
│   │   │   ├── schedule_source_scrape.py
│   │   │   ├── run_manual_scrape.py
│   │   │   ├── parse_snapshot.py
│   │   │   ├── publish_outbound_event.py
│   │   │   └── cleanup_old_snapshots.py
│   ├── scraping/
│   │   ├── browser.py
│   │   ├── fetchers/
│   │   │   ├── playwright_fetcher.py
│   │   │   ├── requests_fetcher.py
│   │   │   └── pdf_fetcher.py
│   │   ├── extractors/
│   │   │   ├── base.py
│   │   │   ├── telecom_extractor.py
│   │   │   ├── banking_extractor.py
│   │   │   ├── insurance_extractor.py
│   │   │   ├── hotels_extractor.py
│   │   │   ├── schools_extractor.py
│   │   │   ├── universities_extractor.py
│   │   │   ├── utilities_extractor.py
│   │   │   ├── solar_extractor.py
│   │   │   └── transport_extractor.py
│   │   ├── parsers/
│   │   │   ├── html_parser.py
│   │   │   ├── table_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   └── text_cleanup.py
│   │   ├── selectors/
│   │   │   ├── econet.yaml
│   │   │   ├── netone.yaml
│   │   │   ├── telecel.yaml
│   │   │   ├── cbz.yaml
│   │   │   ├── old_mutual.yaml
│   │   │   └── ...
│   │   └── normalizers/
│   │       ├── currency.py
│   │       ├── units.py
│   │       ├── text.py
│   │       └── categories.py
│   ├── integrations/
│   │   ├── webhook_client.py
│   │   ├── payload_builders.py
│   │   ├── retry_policy.py
│   │   └── signing.py
│   ├── ui/
│   │   ├── templates/
│   │   │   ├── layout.html
│   │   │   ├── dashboard.html
│   │   │   ├── sources.html
│   │   │   ├── manual_scrape.html
│   │   │   ├── records.html
│   │   │   ├── record_detail.html
│   │   │   └── job_runs.html
│   │   ├── static/
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── img/
│   │   └── viewmodels/
│   ├── utils/
│   │   ├── datetime.py
│   │   ├── hashing.py
│   │   ├── urls.py
│   │   └── enums.py
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       ├── integration/
│       ├── api/
│       └── e2e/
└── examples/
    ├── webhook-payload.json
    ├── manual-scrape-request.json
    └── sample-source-config.yaml
```

## Why this structure works

- `app/api` exposes REST endpoints for admin, scraping, browsing records, and outbound delivery.
- `app/scraping` isolates Playwright, parsers, selectors, and normalization logic.
- `app/workers` handles scheduled scraping, manual scrape jobs, parsing, publishing, and cleanup.
- `app/db/models` stores both raw snapshots and normalized extracted records.
- `docs/` gives your coding agent an implementation path from product intent to production readiness.
- `selectors/*.yaml` lets you change extraction rules without rewriting parser code for every website.

## Core markdown files your agent should use

### 1) `README.md`
Purpose: quick start for humans and agents.

Suggested sections:
- What the system does
- Tech stack
- Local setup
- Environment variables
- Run API / worker / scheduler
- How to add a new source
- How manual scraping works
- How outbound integrations work

Starter content:

```md
# Scraper Hub

Scraper Hub is a Python-based scraping platform that uses Playwright, PostgreSQL, and background workers to collect, normalize, store, review, and distribute pricing/product/tariff data from configured web sources.

## Stack
- Python
- FastAPI
- Playwright
- PostgreSQL
- Alembic
- Redis + Celery/RQ (optional but recommended)
- Jinja/HTMX or React for admin UI

## Main capabilities
- Scheduled source scraping
- Manual URL scraping
- Source-specific extractors and fallback parsing
- Raw snapshot storage
- Normalized records for browsing and search
- Outbound webhook/API publishing to downstream systems

## Local setup
1. Copy `.env.example` to `.env`
2. Start services with `docker-compose up -d`
3. Run migrations
4. Seed initial sources
5. Start API and worker
```

### 2) `docs/00-project-overview.md`
Purpose: one-page project intent.

```md
# Project Overview

## Goal
Build a scraper hub that collects public product, tariff, fee, pricing, and policy data from Zimbabwean telecoms, banks, insurers, hotels, universities, utilities, solar providers, and transport-related sites.

## Outcomes
- Reliable extraction from configured source URLs
- Manual scrape of ad hoc URLs
- Searchable UI page for scraped data
- Outbound integration endpoint/publisher for other systems
- Audit trail of raw vs normalized data

## Users
- Admin users
- Operations/data validation users
- Downstream system integrators
```

### 3) `docs/01-product-requirements.md`
Purpose: concise functional requirements.

```md
# Product Requirements

## Functional requirements
1. Admin can register a source with category, base URL, target pages, frequency, and extractor type.
2. System can scrape configured URLs on a schedule.
3. Admin can submit a manual URL and trigger scrape immediately.
4. System stores raw page snapshot and normalized extracted records.
5. User can view scraped records in a browser page with filters.
6. User can inspect raw snapshot, parse logs, and extraction version.
7. System exposes records via API.
8. System can publish records/events to external systems.
9. System tracks failures, retries, and last successful scrape.
10. System supports per-source parsing rules.

## Non-functional requirements
- Idempotent processing
- Auditable change history
- Retry with backoff
- Secure outbound endpoints
- Observability and alerts
```

### 4) `docs/02-system-architecture.md`
Purpose: target architecture for the agent.

```md
# System Architecture

## Main components
- API service: FastAPI for admin endpoints, data endpoints, UI views
- Worker service: executes scrape and parse jobs
- Scheduler: enqueues recurring source scrapes
- PostgreSQL: stores source configs, raw snapshots, records, events, audit logs
- Redis: queue broker and cache
- Playwright runtime: headless browser for JS-heavy websites

## Flow
1. Scheduler selects due source pages.
2. Worker opens page using Playwright or fallback fetcher.
3. HTML/PDF/raw content snapshot is stored.
4. Parser/extractor normalizes content into records.
5. Records are deduplicated and versioned.
6. Outbound event is created for downstream delivery.
7. UI and API expose latest data and history.
```

### 5) `docs/03-source-catalog.md`
Purpose: inventory of target sources and category mapping.

Use a table like:

```md
# Source Catalog

| Category | Entity | Base URL | Sample Target URL | Extractor Type | Notes |
|---|---|---|---|---|---|
| Telecom | Econet | https://www.econet.co.zw/ | /usd-data-bundles/ | telecom | bundles, voice |
| Telecom | NetOne | https://www.netone.co.zw/ | /data-bundles/ | telecom | check alternate service path |
| Banking | CBZ | https://www.cbz.co.zw/ | /personal-banking/ | banking | products, fees, loans |
| Insurance | Old Mutual | https://www.oldmutual.co.zw/ | /personal/ | insurance | products, pricing |
```

Include fields:
- `entity_name`
- `category`
- `source_type`
- `requires_js`
- `supports_pdf`
- `rate_limit_profile`
- `priority`
- `status`

### 6) `docs/04-data-model.md`
Purpose: entity design before coding.

```md
# Data Model

## Main tables
- sources
- source_pages
- scrape_jobs
- scrape_runs
- raw_snapshots
- extracted_records
- extracted_fields
- webhook_targets
- outbound_events
- audit_logs

## Key relationships
- One source has many source_pages
- One source_page has many scrape_runs
- One scrape_run creates one or more raw_snapshots
- One raw_snapshot produces many extracted_records
- One extracted_record may produce many outbound_events
```

Include expected fields for each table.

### 7) `docs/05-scraping-strategy.md`
Purpose: rules for choosing fetch approach.

```md
# Scraping Strategy

## Fetch modes
- `playwright`: for JS-rendered pages, dynamic tabs, hidden accordions
- `requests`: for static HTML pages
- `pdf`: for downloadable tariffs, fee schedules, brochures

## Extraction strategy order
1. Source-specific structured selectors
2. Generic table extraction
3. Semantic section parsing by headings
4. PDF text/table extraction
5. Manual review flag if confidence is low

## Browser settings
- Headless by default
- User agent rotation optional
- Wait for network idle plus selector readiness
- Capture screenshot on parser failure
```

### 8) `docs/06-parser-rules.md`
Purpose: force consistency in normalization.

```md
# Parser Rules

## Normalized record schema
Each extracted record should contain:
- source_id
- source_page_id
- entity_name
- category
- subcategory
- title
- item_name
- description
- price_value
- price_currency
- billing_period
- unit_value
- unit_type
- eligibility
- effective_date
- captured_at
- source_url
- raw_snapshot_id
- confidence_score

## Normalization rules
- Convert currencies to uppercase ISO-style codes when possible
- Keep original text in raw fields
- Parse bundle sizes into MB/GB units
- Parse voice tariffs into per-minute when possible
- Keep unparsed values in `notes`
```

### 9) `docs/07-api-contracts.md`
Purpose: concrete endpoints for the agent.

```md
# API Contracts

## Admin/source management
- `GET /api/v1/sources`
- `POST /api/v1/sources`
- `PATCH /api/v1/sources/{id}`
- `POST /api/v1/sources/{id}/run`

## Manual scraping
- `POST /api/v1/manual-scrape`
Request:
{
  "url": "https://example.com/page",
  "category": "telecom",
  "extractor_type": "auto",
  "store_result": true
}

## Records
- `GET /api/v1/records`
- `GET /api/v1/records/{id}`
- `GET /api/v1/records/export`

## Job runs
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{id}`

## Integrations
- `GET /api/v1/integrations/targets`
- `POST /api/v1/integrations/targets`
- `POST /api/v1/integrations/publish/{record_id}`
- `POST /api/v1/integrations/publish/batch`
```

### 10) `docs/08-ui-pages.md`
Purpose: define the minimum UI.

```md
# UI Pages

## Dashboard
- Total sources
- Successful scrapes today
- Failed scrapes today
- Records captured today
- Pending outbound deliveries

## Sources page
- List of sources
- Last run status
- Next run time
- Run now action

## Manual scrape page
- URL input
- Category selector
- Extractor selector
- Run scrape button
- Preview of raw text/HTML and normalized records

## Records page
- Filters: category, entity, date, status
- Table of normalized records
- Detail view for record history and raw snapshot
```

### 11) `docs/09-job-orchestration.md`
Purpose: background processing rules.

```md
# Job Orchestration

## Queues
- high: manual scrape, outbound retry
- default: scheduled scrape, parse
- low: cleanup, backfill

## Job lifecycle
queued -> running -> parsed -> published -> completed
queued -> running -> failed -> retrying -> failed_permanent

## Retry rules
- Network failure: retry 3 times with exponential backoff
- Parser mismatch: retry once, then flag for review
- Downstream publish failure: retry 5 times with dead-letter record
```

### 12) `docs/10-error-handling-observability.md`
Purpose: keep the system operable.

```md
# Error Handling and Observability

## Log fields
- trace_id
- source_id
- source_page_id
- scrape_run_id
- url
- extractor_type
- status
- duration_ms

## Metrics
- scrape success rate
- parse success rate
- median scrape duration
- publish success rate
- records extracted per source

## Alerts
- source fails 3 times consecutively
- publish queue backlog > threshold
- parsing confidence drops below threshold
```

### 13) `docs/11-security-compliance.md`
Purpose: make the agent build guardrails early.

```md
# Security and Compliance

- Respect robots.txt and legal review decisions where required
- Rate limit requests per domain
- Secure admin routes with authentication
- Sign outbound webhooks with HMAC
- Encrypt secrets in environment/secret store
- Keep audit logs for source config changes and manual scrape actions
```

### 14) `docs/12-testing-strategy.md`
Purpose: prevent fragile scrapers.

```md
# Testing Strategy

## Unit tests
- Normalizers
- Parsers
- Payload builders

## Integration tests
- DB repositories
- API endpoints
- Queue jobs

## E2E tests
- Playwright fetch against controlled fixture pages
- Manual scrape flow
- Record publish flow

## Regression pack
- Save sample HTML/PDF fixtures from important sources
- Re-run parsers against fixtures on every change
```

### 15) `docs/13-deployment-runbook.md`
Purpose: move from laptop to production.

```md
# Deployment Runbook

## Environments
- local
- staging
- production

## Required services
- API container
- worker container
- scheduler container
- postgres
- redis
- reverse proxy

## Deployment checklist
- Migrations applied
- Playwright browsers installed
- Seed source catalog loaded
- Health checks passing
- Alerts configured
```

### 16) `docs/14-agent-build-order.md`
Purpose: tell your agent exactly what to build first.

```md
# Agent Build Order

## Phase 1
- Initialize repo
- Set up FastAPI app, config, logging
- Add PostgreSQL connection and Alembic
- Create core models and migrations

## Phase 2
- Build source CRUD endpoints
- Build manual scrape endpoint
- Implement Playwright fetcher
- Save raw snapshots

## Phase 3
- Add extractor base classes
- Add telecom and banking extractors first
- Normalize records into DB
- Add records listing API

## Phase 4
- Build UI pages: dashboard, sources, manual scrape, records
- Add job queue and scheduler
- Add retries and alerts

## Phase 5
- Add outbound integration targets
- Add signed webhook publishing
- Add replay and dead-letter handling
- Add tests and production hardening
```

### 17) `docs/15-definition-of-done.md`
Purpose: define completion clearly.

```md
# Definition of Done

A feature is done when:
- Code is merged
- Migration exists if schema changed
- API schema is documented
- Tests pass
- Logs and metrics are added
- Failure path is handled
- UI path is usable where applicable
- README/docs updated
```

## Extra files worth creating

### `.env.example`
```env
APP_ENV=local
APP_NAME=Scraper Hub
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/scraper_hub
REDIS_URL=redis://localhost:6379/0
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT_MS=45000
WEBHOOK_SIGNING_SECRET=change-me
DEFAULT_TIMEZONE=Africa/Harare
```

### `examples/sample-source-config.yaml`
```yaml
name: Econet Data Bundles
entity_name: Econet Wireless
category: telecom
extractor_type: telecom
base_url: https://www.econet.co.zw/
pages:
  - url: https://www.econet.co.zw/usd-data-bundles/
    page_type: data_bundles
    fetch_mode: playwright
    enabled: true
  - url: https://www.econet.co.zw/voice/
    page_type: voice_rates
    fetch_mode: playwright
    enabled: true
schedule:
  cron: "0 */6 * * *"
rate_limit:
  requests_per_minute: 10
```

### `examples/webhook-payload.json`
```json
{
  "event_type": "record.created",
  "record_id": "uuid",
  "entity_name": "Econet Wireless",
  "category": "telecom",
  "subcategory": "data_bundle",
  "title": "Daily Data Bundle",
  "price_value": 1.0,
  "price_currency": "USD",
  "source_url": "https://www.econet.co.zw/usd-data-bundles/",
  "captured_at": "2026-04-17T10:00:00Z"
}
```

## Best way to use these docs with your coding agent

Give the agent this order:
1. Read `docs/00-project-overview.md`
2. Read `docs/02-system-architecture.md`
3. Read `docs/04-data-model.md`
4. Read `docs/07-api-contracts.md`
5. Read `docs/14-agent-build-order.md`
6. Build one phase at a time and update docs after each phase

## Recommended first implementation slice

Start with this thin vertical slice:
- source CRUD
- manual URL scrape endpoint
- Playwright fetch of one telecom page
- raw snapshot persistence
- normalized record extraction
- records list page
- outbound webhook publish for one record

That slice proves the whole platform before scaling to all listed sources.

