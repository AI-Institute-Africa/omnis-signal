import urllib.request
import urllib.parse
import json

TEST_URLS = [
    {"url": "https://www.oldmutual.co.za/personal/solutions/life-and-family/life-insurance/", "category": "insurance"},
    {"url": "https://www.marriott.com/en-us/hotels/hrezw-meikles-hotel/overview/", "category": "hotels"},
    {"url": "https://www.uct.ac.za/students/fees-funding/tuition-fees", "category": "education"},
    {"url": "https://www.ethiopianairlines.com/aa/book/booking/book-flight", "category": "transport"}
]

print("=== Testing New Extractors ===")

for test in TEST_URLS:
    print(f"\nTesting: {test['url']} ({test['category']})")
    try:
        form_data = urllib.parse.urlencode({
            'url': test['url'],
            'category': test['category'],
            'store_result': 'true'
        }).encode('utf-8')

        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/v1/manual-scrape/',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Message: {result.get('message')}")
            print(f"Extracted Records: {result['extracted_records_count']}")
            if result['extracted_records_count'] > 0:
                print("First record sample:")
                # We can't easily see the records from this response, but we can check the DB later
    except Exception as e:
        print(f"Error: {e}")

print("\n=== Test Complete ===")
