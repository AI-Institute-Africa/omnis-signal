import urllib.request
import json

# Get sources to see what URLs we're scraping
with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/', timeout=10) as response:
    sources = json.loads(response.read().decode())

print('SOURCES BEING SCRAPED:')
for source in sources[:10]:  # Show first 10
    print(f'{source["id"]:2d}: {source["name"][:40]:<40} | {source["category"]:<10} | {source["base_url"]}')
if len(sources) > 10:
    print(f'... and {len(sources)-10} more')
print()

# Check if we can get raw snapshots
try:
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/raw-snapshots/', timeout=10) as response:
        snapshots = json.loads(response.read().decode())

    print(f'RAW SNAPSHOTS: {len(snapshots)} total')
    if snapshots:
        # Show latest snapshot
        latest = snapshots[-1]
        print(f'Latest snapshot: {latest["url"]}')
        print(f'Content length: {len(latest.get("content", ""))} chars')
        print(f'Content type: {latest.get("content_type", "unknown")}')
        print(f'Created: {latest.get("created_at", "unknown")}')

        # Show a sample of the content
        content = latest.get('content', '')[:500]
        print(f'Content preview: {content}...')

except Exception as e:
    print(f'Could not get raw snapshots: {e}')