import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/v1/webhook-targets/') as response:
        data = json.loads(response.read().decode())
        print(f'Webhook targets found: {len(data)}')
        for target in data:
            print(f'- {target["name"]}: {target["url"]} (Active: {target["is_active"]})')
except Exception as e:
    print(f'Error: {e}')