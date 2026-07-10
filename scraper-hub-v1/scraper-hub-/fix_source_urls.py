import urllib.request
import json

def fix_critical_source_urls():
    """Update source URLs to point to actual product/service pages instead of homepages"""

    print("FIXING CRITICAL SOURCE URLs")
    print("=" * 50)

    # Current sources that need fixing (based on validation)
    url_updates = {
        # Banking - point to accounts/products pages
        "HSBC UK": "https://www.hsbc.co.uk/personal/credit-cards/",
        "Barclays UK": "https://www.barclays.co.uk/personal/credit-cards/",
        "Lloyds Bank": "https://www.lloydsbank.com/personal/credit-cards/",

        # Telecom - point to plans/bundles pages
        "Vodafone UK": "https://www.vodafone.co.uk/mobile/phones/pay-monthly-plans",
        "O2 UK": "https://www.o2.co.uk/shop/pay-monthly-phones",
        "EE UK": "https://ee.co.uk/pay-monthly",

        # Zimbabwe Telecom - point to data bundles
        "Econet Wireless": "https://www.econet.co.zw/usd-data-bundles/",
        "NetOne Zimbabwe": "https://www.netone.co.zw/personal/data-bundles",

        # Universities - point to fees pages
        "University of Zimbabwe": "https://www.uz.ac.zw/fees-structure/",
        "National University of Science and Technology": "https://www.nust.ac.zw/fees/",
        "Midlands State University": "https://www.msu.ac.zw/fees-structure/",

        # Insurance - point to products
        "Old Mutual Zimbabwe": "https://www.oldmutual.co.zw/personal/products/",
        "NICO General Insurance": "https://www.nico.co.zw/products/",
        "Zimnat Insurance": "https://www.zimnat.co.zw/personal/"
    }

    # Get current sources
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/', timeout=10) as response:
        sources = json.loads(response.read().decode())

    print(f"Found {len(sources)} sources, checking for updates...")

    updated_count = 0
    for source in sources:
        source_name = source['name']
        if source_name in url_updates:
            new_url = url_updates[source_name]
            if source['base_url'] != new_url:
                # Update the source
                update_data = {"base_url": new_url}
                data = json.dumps(update_data).encode('utf-8')

                req = urllib.request.Request(
                    f"http://127.0.0.1:8000/api/v1/sources/{source['id']}",
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='PATCH'
                )

                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.getcode() == 200:
                            print(f"Updated {source_name}")
                            print(f"   {source['base_url']} → {new_url}")
                            updated_count += 1
                        else:
                            print(f"Failed to update {source_name}")
                except Exception as e:
                    print(f"Error updating {source_name}: {e}")
            else:
                print(f"  {source_name} already correct")

    print(f"\nUpdated {updated_count} source URLs")
    print("\nNext steps:")
    print("1. Run: python test_zimbabwe_sources.py")
    print("2. Check if data extraction improved")
    print("3. Run: python validate_extraction.py")
    print("4. Review VALIDATION_REPORT.md for further fixes")

if __name__ == "__main__":
    fix_critical_source_urls()