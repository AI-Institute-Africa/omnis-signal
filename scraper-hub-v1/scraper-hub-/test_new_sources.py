import urllib.request
import urllib.parse
import json
import time
from collections import defaultdict

def test_new_sources():
    """Test the newly added sources from category refinement"""
    print("🧪 Testing New Sources from Category Refinement")
    print("=" * 55)

    try:
        # Get all sources
        with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/', timeout=10) as response:
            all_sources = json.loads(response.read().decode())

        # Filter to only the new sources (IDs 59-71)
        new_sources = [s for s in all_sources if s['id'] >= 59]

        print(f"Testing {len(new_sources)} new sources (IDs 59-71)\n")

        results = defaultdict(lambda: {'tested': 0, 'success': 0, 'records': 0, 'errors': 0})

        for i, source in enumerate(new_sources, 1):
            category = source['category']
            results[category]['tested'] += 1

            print(f"[{i:2d}/{len(new_sources)}] {source['name'][:50]:<50} ", end="")

            try:
                # Test scraping
                data = urllib.parse.urlencode({
                    'url': source['base_url'],
                    'category': category,
                    'extractor_type': 'auto',
                    'store_result': 'true'
                }).encode('utf-8')

                req = urllib.request.Request(
                    'http://127.0.0.1:8000/api/v1/manual-scrape/',
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )

                with urllib.request.urlopen(req, timeout=30) as response:
                    if response.getcode() == 200:
                        result = json.loads(response.read().decode())
                        records_count = result.get('records_extracted', 0)

                        if records_count > 0:
                            print(f"✅ {records_count:3d} records")
                            results[category]['success'] += 1
                            results[category]['records'] += records_count
                        else:
                            print(f"⚠️  {records_count:3d} records")
                    else:
                        print(f"❌ HTTP {response.getcode()}")
                        results[category]['errors'] += 1

            except Exception as e:
                print(f"❌ Error: {str(e)[:20]}...")
                results[category]['errors'] += 1

            # Small delay to be respectful
            time.sleep(0.5)

        # Summary
        print(f"\n{'='*55}")
        print(f"📊 NEW SOURCES TEST RESULTS")
        print(f"{'='*55}")

        total_tested = sum(cat['tested'] for cat in results.values())
        total_success = sum(cat['success'] for cat in results.values())
        total_records = sum(cat['records'] for cat in results.values())
        total_errors = sum(cat['errors'] for cat in results.values())

        print(f"Total Tested: {total_tested}")
        print(f"Successful:   {total_success}/{total_tested} ({total_success/total_tested*100:.1f}%)")
        print(f"Total Records: {total_records}")
        print(f"Errors:       {total_errors}")

        print(f"\n📋 BY CATEGORY")
        print(f"{'Category':<12} | {'Tested':<6} | {'Success':<7} | {'Records':<7} | {'Rate':<5}")
        print(f"{'-'*12}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}-+-{'-'*5}")

        for category in sorted(results.keys()):
            cat_data = results[category]
            success_rate = cat_data['success']/cat_data['tested']*100 if cat_data['tested'] > 0 else 0
            print(f"{category.upper():<12} | {cat_data['tested']:<6} | {cat_data['success']:<7} | {cat_data['records']:<7} | {success_rate:<5.1f}%")

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_new_sources()