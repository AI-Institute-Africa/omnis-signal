import httpx

response = httpx.get('http://localhost:8000/api/v1/records/')
print(f'Status: {response.status_code}')
data = response.json()
print(f'Found {len(data)} records')
for r in data[:3]:
    print(f'- {r["entity_name"]}: {r["title"]} (£{r["price_value"]})')