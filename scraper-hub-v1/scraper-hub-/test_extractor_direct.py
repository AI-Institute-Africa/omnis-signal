import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scraping.extractors.banking import BankingExtractor
from app.db.models.raw_snapshot import RawSnapshot

print('🧪 TESTING BANKING EXTRACTOR DIRECTLY')
print('=' * 50)

# Test URLs
test_urls = [
    'https://www.hsbc.co.uk/credit-cards/',
    'https://www.stanbicbank.co.zw/zimbabwe/personal/',
]

for url in test_urls:
    print(f'Testing: {url}')

    try:
        # Create a mock snapshot (we'll simulate the content)
        snapshot = RawSnapshot(
            url=url,
            content='<html><body><h1>Credit Cards</h1><p>HSBC Credit Card with 0% APR for 12 months</p><div class="price">£25 annual fee</div></body></html>',
            content_type='html'
        )

        # Create extractor
        extractor = BankingExtractor(snapshot)

        # Extract records
        records = extractor.extract()

        print(f'   ✅ Extracted {len(records)} records')

        # Show sample records
        for i, record in enumerate(records[:2]):
            print(f'      {i+1}. [{record.subcategory}] {record.title} - {record.price_currency} {record.price_value or 0:.2f}')

    except Exception as e:
        print(f'   ❌ Error: {str(e)[:100]}...')

print('Test completed.')