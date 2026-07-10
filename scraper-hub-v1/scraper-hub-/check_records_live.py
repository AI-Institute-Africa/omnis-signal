import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/records/') as response:
        data = json.loads(response.read().decode())
        print(f'Records found: {len(data)}')
        for record in data[:10]:  # Show more records
            currency = record.get("price_currency", "$")
            print(f'- {record["entity_name"]}: {record["title"]} ({currency}{record["price_value"]}) - {record["category"]}')
except Exception as e:
    print(f'Error: {e}')