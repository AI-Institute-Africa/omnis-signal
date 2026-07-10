import urllib.request
import urllib.parse
import json
import time

print('🧪 TESTING IMPROVED TELECOM EXTRACTOR ON REAL DATA')
print('=' * 60)

# Test the improved telecom extractor on real URLs
test_cases = [
    {'name': 'Vodafone UK Plans', 'url': 'https://www.vodafone.co.uk/mobile/phones/pay-monthly-plans', 'category': 'telecom'},
    {'name': 'O2 UK Plans', 'url': 'https://www.o2.co.uk/shop/pay-monthly-phones', 'category': 'telecom'},
]

for test_case in test_cases:
    print(f'Testing {test_case["name"]}')

    try:
        data = urllib.parse.urlencode({
            'url': test_case['url'],
            'category': test_case['category'],
            'extractor_type': 'auto',
            'store_result': 'true'
        }).encode('utf-8')

        req = urllib.request.Request(
            'http://127.0.0.1:8001/api/v1/manual-scrape/',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        with urllib.request.urlopen(req, timeout=60) as response:  # Increased timeout for real scraping
            result = json.loads(response.read().decode())
            records_count = result.get('records_extracted', 0)
            print(f'   ✅ Extracted {records_count} records')

            # Show sample records if any
            if 'records' in result and result['records']:
                print('   📋 Sample records:')
                for i, record in enumerate(result['records'][:3]):
                    title = record.get('title', 'N/A')[:60]
                    price = record.get('price_value', 0) or 0
                    currency = record.get('price_currency', 'GBP')
                    subcategory = record.get('subcategory', 'N/A')
                    print(f'      {i+1}. [{subcategory}] {title} - {currency} {price:.2f}')

    except Exception as e:
        print(f'   ❌ Error: {str(e)[:80]}...')

    time.sleep(2)  # Brief pause between requests

print('Test completed. Run validation to check quality improvements.')