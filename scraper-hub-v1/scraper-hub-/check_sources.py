import httpx

response = httpx.get('http://localhost:8000/api/v1/sources/')
print(f'Status: {response.status_code}')
data = response.json()
print(f'Created {len(data)} sources:')
for s in data:
    print(f'- {s["name"]} ({s["category"]})')