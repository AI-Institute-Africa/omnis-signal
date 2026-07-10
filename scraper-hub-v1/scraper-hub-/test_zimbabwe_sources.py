import urllib.request
import urllib.parse
import json

print("=== Testing Zimbabwe Sources ===\n")

# Get all sources first
try:
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/') as response:
        sources = json.loads(response.read().decode())
        print(f'Total sources in system: {len(sources)}')
except Exception as e:
    print(f'Error getting sources: {e}')
    exit(1)

# Test each source
categories = {}
tested = 0
successful = 0
extracted_total = 0

for source in sources:
    tested += 1
    print(f"\n[{tested}/{len(sources)}] Testing: {source['name']}")
    print(f"  URL: {source['base_url']}")
    print(f"  Category: {source['category']}")
    
    try:
        form_data = urllib.parse.urlencode({
            'url': source['base_url'],
            'category': source['category'],
            'store_result': 'true'
        }).encode('utf-8')

        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/v1/manual-scrape/',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode())
            content_length = result["content_length"]
            records = result["extracted_records_count"]
            
            successful += 1
            extracted_total += records
            
            status = "✅" if records > 0 else "⚠️"
            print(f"  {status} Fetched: {content_length} bytes, Extracted: {records} records")
            
            if source['category'] not in categories:
                categories[source['category']] = {'tested': 0, 'success': 0, 'records': 0}
            categories[source['category']]['tested'] += 1
            categories[source['category']]['success'] += 1
            categories[source['category']]['records'] += records
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:80]}...")
        if source['category'] not in categories:
            categories[source['category']] = {'tested': 0, 'success': 0, 'records': 0}
        categories[source['category']]['tested'] += 1

print("\n" + "="*60)
print("=== Test Summary ===")
print(f"\nTotal tested: {tested}")
print(f"Successful: {successful}/{tested} ({int(successful/tested*100)}%)")
print(f"Total records extracted: {extracted_total}")

print("\n=== By Category ===")
for cat, stats in sorted(categories.items()):
    success_rate = int(stats['success']/stats['tested']*100) if stats['tested'] > 0 else 0
    print(f"\n{cat.upper()}:")
    print(f"  Tested: {stats['tested']}")
    print(f"  Success: {stats['success']}/{stats['tested']} ({success_rate}%)")
    print(f"  Records extracted: {stats['records']}")

# Get final record count
try:
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/records/') as response:
        records = json.loads(response.read().decode())
        print(f"\n=== Database Status ===")
        print(f"Total records in database: {len(records)}")
except Exception as e:
    print(f'Error getting records: {e}')