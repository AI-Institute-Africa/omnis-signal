import urllib.request
import json

print("=== Checking Configured Sources ===")
try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/sources/') as response:
        sources = json.loads(response.read().decode())
        print(f'Configured sources: {len(sources)}')
        for source in sources:
            print(f'- {source["name"]} ({source["category"]}) - {source["base_url"]} - Schedule: {source.get("schedule", "None")}')
except Exception as e:
    print(f'Error: {e}')

print("\n=== Checking Current Records ===")
try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/records/') as response:
        records = json.loads(response.read().decode())
        print(f'Current records: {len(records)}')
        if records:
            print('Latest records:')
            for record in records[-3:]:  # Show last 3
                print(f'  - {record["entity_name"]}: {record["title"]} (£{record.get("price_value", 0) or 0})')
except Exception as e:
    print(f'Error: {e}')

print("\n=== Testing All Scrapers ===")
# Test each source by triggering a manual scrape
import urllib.parse

for source in sources:
    print(f"\nTesting {source['name']} ({source['category']}) - {source['base_url']}")
    try:
        # Send form data instead of JSON
        form_data = urllib.parse.urlencode({
            'url': source['base_url'],
            'category': source['category'],
            'store_result': 'true'
        }).encode('utf-8')

        req = urllib.request.Request(
            'http://localhost:8000/api/v1/manual-scrape/',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f'  ✅ Scraped successfully: {result["content_length"]} bytes, {result["extracted_records_count"]} records extracted')
    except Exception as e:
        print(f'  ❌ Error scraping {source["name"]}: {e}')

print("\n=== Final Records Count ===")
try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/records/') as response:
        final_records = json.loads(response.read().decode())
        print(f'Final records: {len(final_records)} (added {len(final_records) - len(records) if "records" in locals() else 0} new records)')
        if len(final_records) > len(records) if "records" in locals() else 0:
            print('New records added:')
            for record in final_records[len(records) if "records" in locals() else 0:]:
                print(f'  - {record["entity_name"]}: {record["title"]} (£{record.get("price_value", 0) or 0}) - {record["category"]}')
except Exception as e:
    print(f'Error checking final records: {e}')