# Zimbabwe Scraper Hub - Quick Reference Guide

## 🚀 System Overview

The Scraper Hub has been expanded to include **52 new Zimbabwe sources** across 8 categories, bringing the total to **58 sources** from UK and Zimbabwe.

## 📋 Sources Configuration

### How Sources Were Added

All sources were added via API with scheduled daily/weekly scraping:

```bash
# Run to add all Zimbabwe sources
python add_zimbabwe_sources.py

# Verify sources were added
python verify_sources_added.py

# Test all sources
python test_zimbabwe_sources.py
```

### Source Categories & Schedules

| Category | Sources | Schedule | Status |
|----------|---------|----------|--------|
| **Telecom** | 12 | Daily 7-9 AM | ✅ Working (50% success) |
| **Banking** | 15 | Daily 10-3 PM | ✅ Working (53% success, 274 records) |
| **Insurance** | 10 | Weekly Monday | ⚠️ Partial (50% success) |
| **Education** | 8 | Weekly Tuesday | ⚠️ Partial (50% success) |
| **Utilities** | 4 | Weekly Wednesday | ❌ Limited (25% success) |
| **Energy** | 3 | Weekly Wednesday | ❌ Limited (33% success) |
| **Hotels** | 4 | Daily 12-3 PM | ❌ Limited (25% success) |
| **Transport** | 2 | Weekly Wednesday | ✅ Working (100% success) |

## 🎯 Top Performing Sources

### By Records Extracted
1. **Stanbic Bank Zimbabwe** - 118 records ⭐⭐⭐
2. **Stanbic Personal Banking** - 118 records ⭐⭐⭐
3. **Vodafone UK** - 50 records ⭐⭐
4. **HSBC UK** - 32 records ⭐⭐
5. **ZB Personal Banking** - 6 records ⭐

### By Accessibility
- **Fully Accessible**: Stanbic, Vodafone, HSBC, ZB, Transport
- **Partially Accessible**: Telecom, Insurance, Education
- **Blocked/Limited**: Hotels, Utilities, Energy, Some Banking

## 📊 Current Statistics

```
Total Sources: 58
Successfully Scraped: 28 (48%)
Failed to Scrape: 30 (52%)
Total Records Extracted: 324
Database Records: 100+
```

## 🔧 Managing Sources

### Adding a New Source

```python
import urllib.request
import json

source_data = {
    "name": "Company Name",
    "category": "telecom|banking|insurance|hotels|education|utilities|energy|transport",
    "base_url": "https://example.com/",
    "schedule": "0 9 * * *"  # Cron format
}

data = json.dumps(source_data).encode('utf-8')
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/sources/',
    data=data,
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(f"Added source ID: {result['id']}")
```

### Manual Scraping a Source

```python
import urllib.request
import urllib.parse
import json

form_data = urllib.parse.urlencode({
    'url': 'https://www.econet.co.zw/',
    'category': 'telecom',
    'store_result': 'true'
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/manual-scrape/',
    data=form_data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(f"Extracted {result['extracted_records_count']} records")
```

## 🌐 Web Interface

Access the Scraper Hub at: **http://127.0.0.1:8000**

### Pages
- **Dashboard** (`/`) - Overview of system status
- **Sources** (`/sources`) - View all configured sources
- **Manual Scrape** (`/manual-scrape`) - Manually scrape any URL
- **Records** (`/records`) - View all extracted records

## ⏰ Cron Schedule Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *

Examples:
0 9 * * *   = Daily at 9 AM
0 10 * * *  = Daily at 10 AM
0 7 * * 1   = Weekly Monday at 7 AM
0 12 * * 3  = Weekly Wednesday at 12 PM
```

## 🐛 Troubleshooting

### Source Returns HTTP 500 Error
- **Cause**: Server blocking requests or site issue
- **Solution**: Try alternative URL or different time
- **Example**: CBZ Bank (blocked), but ZB Bank (works)

### No Records Extracted
- **Cause**: Page structure doesn't match extractor patterns
- **Solution**: Check page HTML for structured data (pricing, tables)
- **Note**: These sources often have pricing in JavaScript or behind auth

### Request Timeout
- **Cause**: Server is slow or unresponsive
- **Solution**: Website may have timeout protections; retry later
- **Typical**: Hotels, Utilities during peak times

## 📈 Performance Metrics

### Scraping Success Rate by Region
- **UK Sources**: 60% (Vodafone, HSBC working well)
- **Zimbabwe Sources**: 42% (Stanbic strongest)
- **Overall**: 48%

### Data Extraction Efficiency
- **High**: Stanbic (118 records), Vodafone (50), HSBC (32)
- **Medium**: ZB Bank (6 records)
- **Low**: Most insurance, education, utilities (0 records)

## 🔐 API Endpoints

```
GET  /api/v1/sources/               - List all sources
POST /api/v1/sources/               - Create new source
GET  /api/v1/sources/{id}           - Get source details
PATCH /api/v1/sources/{id}          - Update source
DELETE /api/v1/sources/{id}         - Delete source

POST /api/v1/manual-scrape/         - Manually scrape URL

GET  /api/v1/records/               - List all records
GET  /api/v1/records/{id}           - Get record details

GET  /api/v1/webhook-targets/       - List webhook targets
POST /api/v1/webhook-targets/       - Create webhook target

GET  /health                         - Check server health
```

## 🚨 Important Notes

1. **Zimbabwe Time Zone**: Sources use UTC+2 time zone for scheduling
2. **Rate Limiting**: Some sites may have request rate limits; currently running with default timeouts
3. **Webhook Publishing**: Extracted records are published to configured webhook targets
4. **Data Storage**: All raw snapshots and extracted records stored in SQLite
5. **Automated Scheduling**: Jobs run via APScheduler; server must be running

## 📝 Recent Test Results

- **Test Date**: April 20, 2026
- **Sources Tested**: 58
- **Success Rate**: 48%
- **Records Extracted**: 324+
- **Best Performer**: Stanbic Bank Zimbabwe (118 records)
- **Worst Category**: Hotels (25% success)

## 🎬 Next Steps

1. Monitor automated scheduled scrapes
2. Review extracted data quality
3. Adjust extractors for Zimbabwe-specific formats
4. Consider adding backup URLs for failing sources
5. Set up alerts for extraction success rates