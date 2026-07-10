import urllib.request
import urllib.parse
import json

print('🧪 TESTING UPDATED SOURCES')
print('=' * 40)

# Test a few key updated sources with their new URLs
test_cases = [
    {'name': 'Vodafone UK', 'url': 'https://www.vodafone.co.uk/mobile/phones/pay-monthly-plans', 'category': 'telecom'},
    {'name': 'HSBC UK', 'url': 'https://www.hsbc.co.uk/personal/credit-cards/', 'category': 'banking'},
    {'name': 'ZIMSEC', 'url': 'https://www.zimsec.co.zw/', 'category': 'schools'}
]

for test_case in test_cases:
    print(f'\n📍 Testing {test_case["name"]}')

    try:
        # Scrape directly
        data = urllib.parse.urlencode({
            'url': test_case['url'],
            'category': test_case['category'],
            'extractor_type': 'auto',
            'store_result': 'true'
        }).encode('utf-8')

        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/v1/manual-scrape/',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            records_count = result.get('records_extracted', 0)
            print(f'   ✅ Fetched content, extracted {records_count} records')

    except Exception as e:
        print(f'   ❌ Error: {str(e)[:50]}...')

print('\n💡 Run full validation: python validate_extraction.py')