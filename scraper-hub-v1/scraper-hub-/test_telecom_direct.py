import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scraping.extractors.telecom import TelecomExtractor
from app.db.models.raw_snapshot import RawSnapshot

print('🧪 TESTING TELECOM EXTRACTOR DIRECTLY')
print('=' * 50)

# Test URLs
test_urls = [
    'https://www.vodafone.co.uk/mobile/phones/pay-monthly-plans',
    'https://www.airtel.co.zw/personal/mobile-plans',
]

for url in test_urls:
    print(f'Testing: {url}')

    try:
        # Create a mock snapshot with telecom content
        snapshot = RawSnapshot(
            url=url,
            content='<html><body><h1>Mobile Plans</h1><p>Unlimited data plan for $50/month</p><div class="price">$50 per month</div><p>Data bundle: 100GB for $20</p></body></html>',
            content_type='html'
        )

        # Create extractor
        extractor = TelecomExtractor(snapshot)

        # Extract records
        records = extractor.extract()

        print(f'   ✅ Extracted {len(records)} records')

        # Show sample records
        for i, record in enumerate(records[:2]):
            print(f'      {i+1}. [{record.subcategory}] {record.title} - {record.price_currency} {record.price_value or 0:.2f}')

    except Exception as e:
        print(f'   ❌ Error: {str(e)[:100]}...')

print('Test completed.')