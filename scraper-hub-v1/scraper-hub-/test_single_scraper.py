import urllib.request
import urllib.parse
import json

print('Testing single scraper (Vodafone)...')
try:
    # Test Vodafone first
    form_data = urllib.parse.urlencode({
        'url': 'https://www.vodafone.co.uk',
        'category': 'telecom',
        'store_result': 'true'
    }).encode('utf-8')

    req = urllib.request.Request(
        'http://localhost:8000/api/v1/manual-scrape/',
        data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f'✅ Vodafone scraped successfully: {result["content_length"]} bytes, {result["extracted_records_count"]} records')
except Exception as e:
    print(f'❌ Error: {e}')