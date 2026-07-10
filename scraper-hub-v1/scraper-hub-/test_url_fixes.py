import urllib.request
import urllib.parse
import json
import time

def test_url_fixes():
    """Test the updated URLs to ensure they work and extract better data"""

    print("🧪 TESTING URL FIXES")
    print("=" * 40)

    # Test key updated sources
    test_cases = [
        # Banking - should now get credit card data
        {'name': 'HSBC UK', 'url': 'https://www.hsbc.co.uk/credit-cards/', 'category': 'banking', 'expected': ['credit', 'card', 'fee']},
        {'name': 'Barclays UK', 'url': 'https://www.barclays.co.uk/personal/credit-cards/', 'category': 'banking', 'expected': ['credit', 'card']},
        {'name': 'Stanbic Bank Zimbabwe', 'url': 'https://www.stanbicbank.co.zw/zimbabwe/personal/', 'category': 'banking', 'expected': ['account', 'banking']},

        # Telecom - should now get plan data
        {'name': 'Vodafone UK', 'url': 'https://www.vodafone.co.uk/mobile/phones/pay-monthly-plans', 'category': 'telecom', 'expected': ['plan', 'monthly', 'data']},
        {'name': 'Econet Wireless', 'url': 'https://www.econet.co.zw/usd-data-bundles/', 'category': 'telecom', 'expected': ['data', 'bundle']},

        # Education - should get fee data
        {'name': 'University of Zimbabwe', 'url': 'https://www.uz.ac.zw/fees-structure/', 'category': 'universities', 'expected': ['fee', 'tuition']},
    ]

    results = {'success': 0, 'total': len(test_cases)}

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing {test_case['name']}")
        print(f"   URL: {test_case['url']}")

        try:
            # Test scraping
            data = urllib.parse.urlencode({
                'url': test_case['url'],
                'category': test_case['category'],
                'extractor_type': 'auto',
                'store_result': 'true'
            }).encode('utf-8')

            req = urllib.request.Request(
                'http://127.0.0.1:8000/api/v1/manual-scrape/',
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                records_count = result.get('records_extracted', 0)

                if records_count > 0:
                    print(f"   ✅ SUCCESS: {records_count} records extracted")
                    results['success'] += 1

                    # Check if records contain expected keywords
                    if 'records' in result and result['records']:
                        sample_record = result['records'][0]
                        title = sample_record.get('title', '').lower()
                        desc = sample_record.get('description', '').lower()

                        found_keywords = []
                        for keyword in test_case['expected']:
                            if keyword.lower() in title or keyword.lower() in desc:
                                found_keywords.append(keyword)

                        if found_keywords:
                            print(f"   🎯 Relevant content found: {', '.join(found_keywords)}")
                        else:
                            print(f"   ⚠️  Records extracted but may not be relevant")

                else:
                    print(f"   ⚠️  No records extracted (but page accessible)")

        except Exception as e:
            print(f"   ❌ FAILED: {str(e)[:50]}...")

        time.sleep(1)  # Be respectful

    print(f"\n{'='*40}")
    print(f"📊 URL FIX TEST RESULTS")
    print(f"{'='*40}")
    print(f"Successful: {results['success']}/{results['total']} ({results['success']/results['total']*100:.1f}%)")

    if results['success'] >= results['total'] * 0.7:
        print("✅ GOOD: Most URL fixes working")
        print("   Ready to proceed to category-specific improvements")
    else:
        print("⚠️  POOR: Many URL fixes not working")
        print("   May need to find alternative URLs or improve error handling")

    print(f"\n💡 NEXT: Run 'python validate_extraction.py' to check overall improvement")

if __name__ == "__main__":
    test_url_fixes()