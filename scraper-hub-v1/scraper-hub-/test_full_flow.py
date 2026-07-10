import urllib.request
import json

# Test scraping a page that might have telecom content
data = json.dumps({
    'url': 'https://httpbin.org/html',
    'category': 'telecom',
    'store_result': True
}).encode('utf-8')

try:
    req = urllib.request.Request(
        'http://localhost:8000/api/v1/manual-scrape/',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f'API Response:')
        print(f'- Status: {response.status}')
        print(f'- Content length: {result["content_length"]}')
        print(f'- Extracted records: {result["extracted_records_count"]}')
        print(f'- URL: {result["url"]}')
except Exception as e:
    print(f'Error: {e}')

# Now check if records were added
print("\nChecking records after scrape...")
try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/records/') as response:
        records = json.loads(response.read().decode())
        print(f'Total records now: {len(records)}')
        if len(records) > 3:  # We had 3 before
            print("New records were added!")
            for record in records[-2:]:  # Show last 2 records
                print(f'- {record["entity_name"]}: {record["title"]} (£{record["price_value"] or 0})')
except Exception as e:
    print(f'Error checking records: {e}')