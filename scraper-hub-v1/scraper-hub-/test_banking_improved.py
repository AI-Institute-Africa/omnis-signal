import urllib.request
import urllib.parse
import json

print('🧪 TESTING IMPROVED BANKING EXTRACTOR')
print('=' * 50)

# Test the improved banking extractor
test_cases = [
    {'name': 'HSBC UK', 'url': 'https://www.hsbc.co.uk/credit-cards/', 'category': 'banking'},
    {'name': 'Stanbic Bank Zimbabwe', 'url': 'https://www.stanbicbank.co.zw/zimbabwe/personal/', 'category': 'banking'},
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

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            records_count = result.get('records_extracted', 0)
            print(f'   ✅ Extracted {records_count} records')

            # Show sample records if any
            if 'records' in result and result['records']:
                print('   📋 Sample records:')
                for i, record in enumerate(result['records'][:2]):
                    title = record.get('title', 'N/A')[:60]
                    price = record.get('price_value', 0) or 0
                    currency = record.get('price_currency', 'GBP')
                    subcategory = record.get('subcategory', 'N/A')
                    print(f'      {i+1}. [{subcategory}] {title} - {currency} {price:.2f}')

    except Exception as e:
        print(f'   ❌ Error: {str(e)[:50]}...')

print('Run: python validate_extraction.py')