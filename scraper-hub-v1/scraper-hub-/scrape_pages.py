import httpx

# URLs to scrape from the sources we created
scrape_urls = [
    {'url': 'https://www.vodafone.co.uk/mobile/phones/pay-monthly-contracts', 'category': 'telecom'},
    {'url': 'https://www.o2.co.uk/shop/phones/pay-monthly', 'category': 'telecom'},
    {'url': 'https://www.ee.co.uk/ee-phone-plans', 'category': 'telecom'},
    {'url': 'https://www.hsbc.co.uk/current-accounts/', 'category': 'banking'},
    {'url': 'https://www.barclays.co.uk/current-accounts/', 'category': 'banking'},
    {'url': 'https://www.lloydsbank.com/current-accounts.html', 'category': 'banking'}
]

for item in scrape_urls:
    data = {
        'url': item['url'],
        'category': item['category'],
        'store_result': True
    }
    response = httpx.post('http://localhost:8000/api/v1/manual-scrape/', json=data)
    print(f'Scraped {item["url"]}: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'  - Content length: {result["content_length"]}')
        print(f'  - Extracted records: {result["extracted_records_count"]}')
    else:
        print(f'  - Error: {response.text}')