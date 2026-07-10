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

## Expected fields (to be detailed during implementation)
- sources: id, name, category, base_url, created_at, updated_at
- source_pages: id, source_id, url, page_type, enabled, schedule
- scrape_jobs: id, source_page_id, status, created_at
- scrape_runs: id, job_id, started_at, completed_at, status
- raw_snapshots: id, run_id, url, content, content_type, captured_at
- extracted_records: id, snapshot_id, entity_name, category, title, price_value, etc.
- extracted_fields: id, record_id, field_name, field_value
- webhook_targets: id, name, url, secret, is_active, created_at, updated_at
- webhook_delivery_attempts: id, target_id, record_id, payload, status, attempt_count, error_message, last_attempt_at, created_at
- audit_logs: id, action, entity_type, entity_id, changes, timestamp