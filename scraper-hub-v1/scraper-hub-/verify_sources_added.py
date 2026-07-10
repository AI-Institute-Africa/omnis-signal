import urllib.request
import json

print("=== Verifying Added Sources ===\n")

try:
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/', timeout=10) as response:
        sources = json.loads(response.read().decode())
        
        print(f"Total sources in database: {len(sources)}\n")
        
        # Group by category
        categories = {}
        for source in sources:
            cat = source['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(source['name'])
        
        # Print by category
        for cat in sorted(categories.keys()):
            print(f"{cat.upper()} ({len(categories[cat])} sources):")
            for name in sorted(categories[cat]):
                print(f"  - {name}")
            print()
        
        print(f"=== Summary ===")
        print(f"Total: {len(sources)} sources")
        print(f"Categories: {len(categories)}")
        
except Exception as e:
    print(f'Error: {e}')