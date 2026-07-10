import urllib.request
import urllib.parse
import json
import sys

def scrape(url, category):
    print(f"Scraping {url} as {category}...")
    try:
        form_data = urllib.parse.urlencode({
            'url': url,
            'category': category,
            'store_result': 'true'
        }).encode('utf-8')

        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/v1/manual-scrape/',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())
            print(f"Success!")
            print(f"Records extracted: {result['extracted_records_count']}")
            return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    url = "https://www.econet.co.zw/usd-data-bundles/"
    cat = "telecom"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        cat = sys.argv[2]
    scrape(url, cat)
