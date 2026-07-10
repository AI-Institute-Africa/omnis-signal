import httpx

# Test with simple HTML pages that should work with requests
test_urls = [
    {'url': 'https://httpbin.org/html', 'category': 'test'},
    {'url': 'https://example.com', 'category': 'test'},
]

for item in test_urls:
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