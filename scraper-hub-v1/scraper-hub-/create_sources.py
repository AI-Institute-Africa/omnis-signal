import httpx

sources = [
    {'name': 'Vodafone UK', 'category': 'telecom', 'base_url': 'https://www.vodafone.co.uk', 'schedule': '0 9 * * *'},
    {'name': 'O2 UK', 'category': 'telecom', 'base_url': 'https://www.o2.co.uk', 'schedule': '0 10 * * *'},
    {'name': 'EE UK', 'category': 'telecom', 'base_url': 'https://www.ee.co.uk', 'schedule': '0 11 * * *'},
    {'name': 'HSBC UK', 'category': 'banking', 'base_url': 'https://www.hsbc.co.uk', 'schedule': '0 12 * * *'},
    {'name': 'Barclays UK', 'category': 'banking', 'base_url': 'https://www.barclays.co.uk', 'schedule': '0 13 * * *'},
    {'name': 'Lloyds Bank', 'category': 'banking', 'base_url': 'https://www.lloydsbank.com', 'schedule': '0 14 * * *'}
]

for source in sources:
    response = httpx.post('http://localhost:8000/api/v1/sources/', json=source)
    print(f'Created {source["name"]}: {response.status_code}')
    if response.status_code != 200:
        print(f'Error: {response.text}')