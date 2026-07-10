## Phase 1 ✅
- Initialize repo
- Set up FastAPI app, config, logging
- Add PostgreSQL connection and Alembic
- Create core models and migrations

## Phase 2 ✅
- Build source CRUD endpoints
- Build manual scrape endpoint
- Implement Playwright fetcher
- Save raw snapshots

## Phase 3 ✅
- Add extractor base classes
- Add telecom and banking extractors first
- Normalize records into DB
- Add records listing API

## Phase 4 ✅
- Build UI pages: dashboard, sources, manual scrape, records
- Add job queue and scheduler
- Add retries and alerts

## Phase 5 ✅
- Add outbound integration targets
- Add signed webhook publishing
- Add replay and dead-letter handling
- Add tests and production hardening