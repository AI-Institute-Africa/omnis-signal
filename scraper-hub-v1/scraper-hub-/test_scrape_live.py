import urllib.request
import json

# Test manual scraping
data = json.dumps({
    'url': 'https://httpbin.org/html',
    'category': 'test',
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
        print(f'Manual scrape result:')
        print(f'- Status: {response.status}')
        print(f'- Content length: {result["content_length"]}')
        print(f'- Extracted records: {result["extracted_records_count"]}')
        print(f'- URL: {result["url"]}')
        print('✅ Manual scraping is working!')
except Exception as e:
    print(f'Error: {e}')