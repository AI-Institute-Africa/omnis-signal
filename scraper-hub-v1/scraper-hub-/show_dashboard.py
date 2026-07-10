import urllib.request
import json
from datetime import datetime

print("+" + "="*78 + "+")
print("|" + " "*20 + "SCRAPER HUB - ZIMBABWE SOURCES DASHBOARD" + " "*19 + "|")
print("+" + "="*78 + "+\n")

try:
    # Get sources
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/', timeout=10) as response:
        sources = json.loads(response.read().decode())
    
    # Get records
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/records/', timeout=10) as response:
        records = json.loads(response.read().decode())
    
    print(f"SYSTEM STATUS")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Server: http://127.0.0.1:8000")
    print(f"   Status: OK - OPERATIONAL\n")
    
    print(f"STATISTICS")
    print(f"   Total Sources: {len(sources)}")
    print(f"   Total Records: {len(records)}")
    print(f"   Average Records/Source: {len(records)/len(sources):.1f}\n")
    
    # Get categories
    categories = {}
    for source in sources:
        cat = source['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print(f"SOURCES BY CATEGORY")
    for cat in sorted(categories.keys()):
        print(f"   {cat.upper():12} : {categories[cat]:2} sources")
    
    print(f"\nRECENT RECORDS (Last 10)")
    print(f"   {'Entity':<20} | {'Title':<30} | {'Value':<10} | {'Category':<10}")
    print(f"   {'-'*20}-+-{'-'*30}-+-{'-'*10}-+-{'-'*10}")
    
    for record in records[-10:]:
        entity = record.get('entity_name', 'Unknown')[:20]
        title = record.get('title', 'N/A')[:30]
        currency = record.get('price_currency', '$')
        price = f"{currency}{record.get('price_value', 0) or 0:.2f}"[:10]
        category = record.get('category', 'N/A')[:10]
        print(f"   {entity:<20} | {title:<30} | {price:<10} | {category:<10}")
    
    # Show top performers
    print(f"\nTOP PERFORMING SOURCES")
    entity_records = {}
    for record in records:
        entity = record.get('entity_name', 'Unknown')
        if entity not in entity_records:
            entity_records[entity] = 0
        entity_records[entity] += 1
    
    top_5 = sorted(entity_records.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (entity, count) in enumerate(top_5, 1):
        stars = "*" * min(5, count // 20 + 1)
        print(f"   {i}. {entity:<30} - {count:3} records {stars}")
    
    print(f"\nQUICK LINKS")
    print(f"   Dashboard:     http://127.0.0.1:8000/")
    print(f"   Sources:       http://127.0.0.1:8000/sources")
    print(f"   Manual Scrape: http://127.0.0.1:8000/manual-scrape")
    print(f"   Records:       http://127.0.0.1:8000/records")
    print(f"\nUSEFUL COMMANDS")
    print(f"   python add_zimbabwe_sources.py      - Add sources")
    print(f"   python verify_sources_added.py      - Verify sources")
    print(f"   python test_zimbabwe_sources.py     - Test all sources")
    print(f"\n" + "="*80)
    
except Exception as e:
    print(f"Error: {e}")
    print(f"   Make sure the server is running on http://127.0.0.1:8000")