import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/sources/') as response:
        data = json.loads(response.read().decode())
        print(f'Sources found: {len(data)}')
        for source in data:
            print(f'- {source["name"]} ({source["category"]}) - {source["base_url"]}')
except Exception as e:
    print(f'Error: {e}')