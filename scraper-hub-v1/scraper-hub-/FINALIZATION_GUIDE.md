# Scraper Hub - System Finalization Guide

## Quick Start

### 1. Start the API Server
```bash
# Windows (PowerShell)
.\run.ps1 -Mode api

# Linux/Mac
./run.sh api
```

The API will be available at: **http://localhost:8000**

### 2. Access the Web Dashboard
Open: **http://localhost:8000** to access the web interface

### 3. View System Status
```bash
python dashboard.py
```

### 4. Scrape Data
```bash
# Scrape first 10 sources
python finalize_system.py --scrape-batch 10

# Scrape all banking sources
python finalize_system.py --scrape-batch --scrape-category banking

# Full system finalization
python finalize_system.py --full-finalize
```

### 5. Export Data
```bash
# Export to CSV
python finalize_system.py --export-csv

# Export to JSON
python finalize_system.py --export-json
```

---

## System Architecture

### Components
- **API Server**: FastAPI on port 8000
- **Database**: SQLite (scraper_hub.db) or PostgreSQL
- **Task Queue**: Redis + RQ (optional for async jobs)
- **Scheduler**: APScheduler (integrated in app startup)
- **Browser Automation**: Playwright

### Data Flow
```
Source Configuration 
    ↓
Fetch Page Content (Playwright)
    ↓
Store Raw Snapshot
    ↓
Extract Records (Category-specific Extractors)
    ↓
Normalize & Deduplicate
    ↓
Store Extracted Records
    ↓
Publish to Webhooks (Optional)
```

---

## Current System Status

### Database Statistics
- **Total Sources**: 544
- **Total Pages**: 1,181 (enabled: varies)
- **Raw Snapshots**: Hundreds captured
- **Extracted Records**: 11,345+
  - **With Prices**: 11,155 (98.4%)
  - **Quality Score ≥ 0.75**: ~9,000+

### Data by Category
| Category | Records | % with Price | Status |
|----------|---------|-------------|--------|
| Telecom | ~3,000 | 98% | ✅ Working |
| Banking | ~4,000 | 99% | ✅ Working |
| Insurance | ~1,500 | 95% | ⚠️ Partial |
| Education | ~800 | 90% | ⚠️ Partial |
| Hotels | ~500 | 85% | ⚠️ Limited |
| Utilities | ~700 | 92% | ✅ Working |
| Energy | ~300 | 88% | ⚠️ Limited |
| Transport | ~145 | 100% | ✅ Working |

---

## Key Features

### 1. **Automated Scraping**
- Scheduled daily/weekly scraping based on source configuration
- Automatic retry on failures with exponential backoff
- Browser fingerprinting to avoid detection
- Playwright with random user agents

### 2. **Intelligent Extraction**
- Category-specific extractors for optimal accuracy:
  - **TelecomExtractor**: Mobile plans, data bundles, voice rates
  - **BankingExtractor**: Account types, fees, interest rates
  - **InsuranceExtractor**: Policies, premiums, coverage
  - **HospitalityExtractor**: Room types, rates, facilities
  - **EducationExtractor**: Tuition fees, programs
  - **UtilitiesExtractor**: Tariffs, rates, charges
  - **TransportExtractor**: Fares, schedules, services
  - **GenericExtractor**: Fallback for unstructured content

### 3. **Data Normalization**
- Automatic currency detection
- Unit conversion (GB, MB, etc.)
- Price parsing and validation
- Confidence scoring

### 4. **Quality Assurance**
- Duplicate detection and merging
- Confidence scoring (0.0 - 1.0)
- Data completeness metrics
- Quality categorization:
  - **Good**: price + confidence ≥ 0.75
  - **Partial**: confidence 0.5-0.75
  - **Poor**: confidence < 0.5 or no price

### 5. **Webhook Publishing**
- Push extracted data to external systems
- HMAC signing for security
- Automatic retry on failure
- Failed delivery tracking

### 6. **Web UI Dashboard**
- Overview of sources and records
- Manual URL scraping
- Record browsing and search
- Webhook configuration
- Job monitoring

---

## API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Sources
```bash
# List all sources
GET /api/v1/sources/

# Create a new source
POST /api/v1/sources/
{
  "name": "Source Name",
  "category": "telecom|banking|insurance|hotels|education|utilities|energy|transport",
  "base_url": "https://example.com/",
  "schedule": "0 9 * * *"  # Cron expression (optional)
}

# Get source by ID
GET /api/v1/sources/{source_id}

# Update source
PUT /api/v1/sources/{source_id}

# Delete source
DELETE /api/v1/sources/{source_id}
```

### Source Pages
```bash
# Add pages to a source
POST /api/v1/sources/{source_id}/pages
{
  "urls": ["https://example.com/page1", "https://example.com/page2"]
}
```

### Manual Scraping
```bash
# Scrape a single URL
POST /api/v1/manual-scrape/
{
  "url": "https://example.com/pricing",
  "category": "telecom",
  "extractor_type": "auto",
  "store_result": true
}
```

### Records
```bash
# Get extracted records
GET /api/v1/records/

# Search records
GET /api/v1/records/?entity=Econet&category=telecom&min_price=100&max_price=5000

# Get record by ID
GET /api/v1/records/{record_id}
```

### Webhook Integration
```bash
# Create webhook target
POST /api/v1/webhook-targets/
{
  "name": "My Integration",
  "url": "https://myapp.com/webhooks/scraper",
  "active": true
}

# List webhook deliveries
GET /api/v1/delivery-attempts/

# Replay failed deliveries
POST /api/v1/webhook-targets/{target_id}/replay-failed
```

---

## Configuration

### Environment Variables (.env)
```ini
# Server
APP_ENV=local
APP_NAME=Scraper Hub
API_HOST=0.0.0.0
API_PORT=8000

# Database (uses SQLite by default, or PostgreSQL)
DATABASE_URL=sqlite:///./scraper_hub.db
# For PostgreSQL: postgresql+psycopg://user:pass@localhost:5432/scraper_hub

# Redis (optional, for task queue)
REDIS_URL=redis://localhost:6379/0

# Playwright
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT_MS=45000

# Webhooks
WEBHOOK_SIGNING_SECRET=change-me-to-secure-random-string
WEBHOOK_MAX_RETRIES=3
WEBHOOK_REQUEST_TIMEOUT=30

# Timezone
DEFAULT_TIMEZONE=Africa/Harare

# AI Enrichment (optional)
GEMINI_API_KEY=your-api-key
```

---

## Running the Full System

### Option 1: Single Process (Recommended for Development)
```bash
# Windows
.\run.ps1 -Mode full

# Linux/Mac
./run.sh full
```

This starts:
- API Server on port 8000
- Integrated scheduler (for scheduled scraping)

### Option 2: Separate Processes (Recommended for Production)

Terminal 1 - API Server:
```bash
.\run.ps1 -Mode api
```

Terminal 2 - Background Worker (if using Redis):
```bash
.\run.ps1 -Mode worker
```

Terminal 3 - Scheduler:
```bash
.\run.ps1 -Mode scheduler
```

---

## System Finalization Workflow

### Step 1: Initialize
```bash
python finalize_system.py --init-db
```

### Step 2: Clean Test Data (Optional)
```bash
python finalize_system.py --clean-test-data
```

### Step 3: Verify Configuration
```bash
python finalize_system.py --verify-config
```

### Step 4: Check System Status
```bash
python finalize_system.py --status
```

### Step 5: Run Scrapes
```bash
# Scrape 10 sources
python finalize_system.py --scrape-batch 10

# Scrape all sources (caution: may take hours)
python finalize_system.py --scrape-batch
```

### Step 6: Export Data
```bash
python finalize_system.py --export-csv
python finalize_system.py --export-json
```

### Full Automation
```bash
# Do everything in one command
python finalize_system.py --full-finalize
```

---

## Adding New Sources

### Via API
```python
import json
import urllib.request

source = {
    "name": "New Company",
    "category": "telecom",
    "base_url": "https://company.com/",
    "schedule": "0 9 * * *"  # Daily at 9 AM
}

data = json.dumps(source).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:8000/api/v1/sources/',
    data=data,
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    source_id = result['id']
    
    # Add pages
    pages = {
        "urls": [
            "https://company.com/plans",
            "https://company.com/pricing"
        ]
    }
    
    page_data = json.dumps(pages).encode('utf-8')
    page_req = urllib.request.Request(
        f'http://localhost:8000/api/v1/sources/{source_id}/pages',
        data=page_data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(page_req) as page_response:
        print(f"Source created: {source_id}")
```

### Via Web UI
1. Navigate to http://localhost:8000/sources
2. Click "Add Source"
3. Enter source details
4. Add pages
5. Click "Save"

---

## Troubleshooting

### Issue: "Database is locked"
**Solution**: SQLite with multiple writers. Use PostgreSQL for production.

```bash
# Switch to PostgreSQL
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/scraper_hub
```

### Issue: "Playwright not found"
**Solution**: Install Playwright browsers
```bash
python -m playwright install
```

### Issue: "Connection refused to Redis"
**Solution**: Redis is not required. System works without it (synchronously).

To use Redis:
```bash
# Install Redis locally or use Docker
docker run -d -p 6379:6379 redis
```

### Issue: "Extraction returns 0 records"
**Solution**: Check if:
1. Page URL is correct
2. Page is not blocked
3. Correct extractor for category
4. Content has expected structure

Try manual scraping first:
```bash
curl -X POST http://localhost:8000/api/v1/manual-scrape/ \
  -F "url=https://example.com/pricing" \
  -F "category=telecom" \
  -F "store_result=true"
```

---

## Performance Optimization

### Database Indexing
The system creates indexes on:
- entity_name, category, price_value
- captured_at for time-series queries

### Caching
- Snapshot deduplication
- Record deduplication
- Price change detection

### Scraping Best Practices
1. Set realistic delays between requests
2. Rotate user agents
3. Use headless mode (faster)
4. Batch scrapes in off-peak hours
5. Monitor for IP bans

---

## Data Export Formats

### CSV Export
Fields:
```
Entity, Category, Subcategory, Title, Item Name,
Price, Currency, Billing Period, Unit Value, Unit Type,
Description, Source URL, Confidence Score, Captured At
```

### JSON Export
```json
{
  "export_timestamp": "2026-06-08T09:10:00",
  "total_records": 11155,
  "records": [
    {
      "id": 1,
      "entity_name": "Econet Wireless",
      "category": "telecom",
      "title": "Econet Monthly Data Plan 5GB",
      "price": {
        "value": 25.00,
        "currency": "USD",
        "billing_period": "month"
      },
      "confidence_score": 0.95,
      "captured_at": "2026-06-08T09:10:00"
    }
  ]
}
```

---

## Support & Resources

### Key Files
- **Main App**: `app/main.py`
- **Database Models**: `app/db/models/`
- **Extractors**: `app/scraping/extractors/`
- **API Routes**: `app/api/routes/`
- **Web UI**: `app/templates/` and `app/static/`

### Documentation
- [README.md](README.md) - Project overview
- [scraper_hub_build_guide.md](scraper_hub_build_guide.md) - Architecture guide
- [ZIMBABWE_SOURCES_GUIDE.md](ZIMBABWE_SOURCES_GUIDE.md) - Zimbabwe-specific sources

### Example Scripts
- `finalize_system.py` - System management
- `dashboard.py` - Real-time status
- `test_all_scrapers.py` - Scraper testing
- `test_api_no_store.py` - API testing

---

## Next Steps

1. **Verify System Status**
   ```bash
   python finalize_system.py --status
   ```

2. **Clean Old Test Data**
   ```bash
   python finalize_system.py --clean-test-data
   ```

3. **Start API Server**
   ```bash
   .\run.ps1 -Mode api
   ```

4. **Access Web Dashboard**
   Open: http://localhost:8000

5. **Configure Webhook Integration** (Optional)
   - Set up webhook targets for real-time data delivery
   - Use HMAC signing for security

6. **Set Up Scheduled Scraping**
   - Configure cron schedules per source
   - Sources will automatically scrape on schedule

7. **Monitor and Optimize**
   - Check extraction stats regularly
   - Adjust extractor rules if needed
   - Monitor for blocked sources

---

**System Ready for Production!** ✅

Your Scraper Hub is now finalized and ready to extract real-world price and product data from configured sources.
