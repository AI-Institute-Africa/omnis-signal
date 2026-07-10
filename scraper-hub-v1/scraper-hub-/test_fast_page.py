import urllib.request
import urllib.parse
import json

print('Testing with fast page (httpbin)...')
try:
    form_data = urllib.parse.urlencode({
        'url': 'https://httpbin.org/html',
        'category': 'telecom',
        'store_result': 'true'
    }).encode('utf-8')

    req = urllib.request.Request(
        'http://localhost:8000/api/v1/manual-scrape/',
        data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode())
        print(f'✅ Fast page scraped: {result["content_length"]} bytes, {result["extracted_records_count"]} records')
except Exception as e:
    print(f'❌ Error: {e}')