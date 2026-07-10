# Scraper Hub API Usage

This file explains how external users can connect to and use the Scraper Hub REST API.

## Base URL

When the system is running locally, the API base URL is:

- `http://localhost:8000`

If deployed externally, replace `localhost` with the host name or IP address of the server.

The API is organized into two main versions:

- `GET /health` — basic service health check
- `API v1` endpoints under `/api/v1`
- `API v2` market data endpoints under `/api/v2`

## Starting the API Server

From the `scraper-hub-` project root:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

If you are using the provided startup script:

```powershell
.\run.ps1 full 8000
```

## Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{ "status": "healthy" }
```

## API v1 Endpoints

### Sources

List all sources:

```bash
curl http://localhost:8000/api/v1/sources/
```

Create a new source:

```bash
curl -X POST http://localhost:8000/api/v1/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zimbabwe Telecom",
    "category": "telecom",
    "base_url": "https://example.com",
    "schedule": "0 3 * * *"
  }'
```

Update a source:

```bash
curl -X PATCH http://localhost:8000/api/v1/sources/123 \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "0 4 * * *"
  }'
```

Delete a source:

```bash
curl -X DELETE http://localhost:8000/api/v1/sources/123
```

Trigger a scheduled scrape for a source:

```bash
curl -X POST http://localhost:8000/api/v1/sources/123/scrape
```

Trigger realtime extraction for all configured sources:

```bash
curl -X POST http://localhost:8000/api/v1/sources/realtime
```

### Manual Scrape

This endpoint accepts form data and is intended for one-off page scraping.

```bash
curl -X POST http://localhost:8000/api/v1/manual-scrape/ \
  -F "url=https://example.com/product" \
  -F "category=telecom" \
  -F "extractor_type=auto" \
  -F "store_result=on"
```

Fields:

- `url` — page to scrape
- `category` — category hint for extraction (`telecom`, `banking`, etc.)
- `extractor_type` — `auto` or a specific extractor name
- `store_result` — set to `on` to persist the result
- `content` — optional raw HTML/text content to parse directly without fetching

### Records

Fetch extracted records:

```bash
curl "http://localhost:8000/api/v1/records/?limit=50&offset=0"
```

Filter records by category, entity, or quality:

```bash
curl "http://localhost:8000/api/v1/records/?category=telecom&entity_name=Econet&has_price_only=true"
```

Get a single record:

```bash
curl http://localhost:8000/api/v1/records/456
```

Record filters:

- `category`
- `entity_name`
- `subcategory`
- `min_confidence`
- `verified_only=true`
- `has_price_only=true`
- `limit`
- `offset`

### Webhook Targets

List configured webhook targets:

```bash
curl http://localhost:8000/api/v1/webhook-targets/
```

Create a webhook target:

```bash
curl -X POST http://localhost:8000/api/v1/webhook-targets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Record Delivery",
    "url": "https://webhook-receiver.example.com/target",
    "secret": "super-secret-16-chars",
    "is_active": true
  }'
```

Update a webhook target:

```bash
curl -X PATCH http://localhost:8000/api/v1/webhook-targets/789 \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

Delete a webhook target:

```bash
curl -X DELETE http://localhost:8000/api/v1/webhook-targets/789
```

Replay failed deliveries for a target:

```bash
curl -X POST http://localhost:8000/api/v1/webhook-targets/789/replay-failed
```

Replay all failed webhook deliveries:

```bash
curl -X POST http://localhost:8000/api/v1/webhook-targets/replay-all-failed
```

### Delivery Attempts

View webhook delivery logs:

```bash
curl http://localhost:8000/api/v1/delivery-attempts/
```

## API v2 Market Data Endpoints

The v2 market data endpoints require an API key header:

- Header name: `X-API-Key`

If `MASTER_API_KEY` is not explicitly set, the default development key is `dev-master-key`.

Fetch market data:

```bash
curl -H "X-API-Key: your_api_key_here" \
  "http://localhost:8000/api/v2/market-data?category=telecom&entity_name=Econet&limit=50&offset=0"
```

Fetch latest market data by sector:

```bash
curl -H "X-API-Key: your_api_key_here" \
  "http://localhost:8000/api/v2/market-data/latest-by-sector?categories=telecom&categories=banking&limit_per_category=10"
```

## Example Python Usage

```python
import requests

BASE_URL = "http://localhost:8000"

# List records
resp = requests.get(f"{BASE_URL}/api/v1/records/", params={"category": "telecom", "limit": 20})
print(resp.json())

# Manual scrape
resp = requests.post(
    f"{BASE_URL}/api/v1/manual-scrape/",
    data={
        "url": "https://example.com/offering",
        "category": "telecom",
        "extractor_type": "auto",
        "store_result": "on",
    },
)
print(resp.status_code, resp.text)

# Market data with API key
resp = requests.get(
    f"{BASE_URL}/api/v2/market-data",
    params={"category": "telecom", "limit": 10},
    headers={"X-API-Key": "your_api_key_here"},
)
print(resp.json())
```

## Security and External Access

- Expose `http://<host>:8000` to external users only if the network is trusted.
- For production use, set `MASTER_API_KEY` to a strong secret and use the v2 endpoints with `X-API-Key`.
- If you need to secure v1 endpoints, add authentication middleware or reverse-proxy access control.

## Notes

- `POST /api/v1/manual-scrape/` expects form data rather than JSON.
- The `/api/v1/records/` endpoint is the primary way to retrieve extracted pricing and product records.
- `POST /api/v1/sources/{source_id}/scrape` triggers extraction for a configured source.
