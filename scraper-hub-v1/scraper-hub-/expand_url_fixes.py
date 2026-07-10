import urllib.request
import json

def expand_url_corrections():
    """Expand URL corrections to cover more sources with working product pages"""

    print("🔧 PHASE 1: EXPANDED URL CORRECTIONS")
    print("=" * 50)

    # More comprehensive URL updates - focusing on working product pages
    comprehensive_updates = {
        # UK Banking - Credit Cards (most reliable product pages)
        "HSBC UK": "https://www.hsbc.co.uk/credit-cards/",
        "Barclays UK": "https://www.barclays.co.uk/personal/credit-cards/",
        "Lloyds Bank": "https://www.lloydsbank.com/personal/save-with-us/credit-cards/",

        # UK Telecom - Mobile plans (specific product pages)
        "Vodafone UK": "https://www.vodafone.co.uk/mobile/phones/pay-monthly-plans",
        "O2 UK": "https://www.o2.co.uk/shop/pay-monthly-phones",
        "EE UK": "https://ee.co.uk/pay-monthly",

        # Zimbabwe Banking - Personal banking pages
        "Stanbic Bank Zimbabwe": "https://www.stanbicbank.co.zw/zimbabwe/personal/",
        "ZB Bank": "https://www.zb.co.zw/personal-banking/",
        "CBZ Bank": "https://www.cbz.co.zw/personal/",
        "CBZ Personal Banking": "https://www.cbz.co.zw/personal/personal-banking/",

        # Zimbabwe Telecom - Data bundles and plans
        "Econet Wireless": "https://www.econet.co.zw/usd-data-bundles/",
        "Econet Data Bundles": "https://www.econet.co.zw/usd-data-bundles/",
        "Econet Voice Rates": "https://www.econet.co.zw/voice/",
        "NetOne Zimbabwe": "https://www.netone.co.zw/personal/data-bundles",
        "Telecel Zimbabwe": "https://www.telecel.co.zw/personal",

        # Education - Fees and programs (where available)
        "University of Zimbabwe": "https://www.uz.ac.zw/fees-structure/",
        "National University of Science and Technology": "https://www.nust.ac.zw/fees/",
        "Midlands State University": "https://www.msu.ac.zw/fees-structure/",
        "Great Zimbabwe University": "https://www.gzu.ac.zw/fees/",
        "Chinhoyi University of Technology": "https://www.cut.ac.zw/fees/",
        "Zimbabwe Schools Examination Council (ZIMSEC)": "https://www.zimsec.co.zw/",
        "Ministry of Primary and Secondary Education": "https://www.mopsce.gov.zw/",

        # Insurance - Products pages
        "Old Mutual Zimbabwe": "https://www.oldmutual.co.zw/personal/products/",
        "NICO General Insurance": "https://www.nico.co.zw/products/",
        "Zimnat Insurance": "https://www.zimnat.co.zw/personal/",
        "Fidelity Life Assurance": "https://www.fidelitylife.co.zw/products/",
        "Britam Zimbabwe": "https://www.britam.com/zimbabwe/personal/",

        # Utilities - Services pages
        "Zimbabwe Electricity Supply Authority (ZESA)": "https://www.zesa.co.zw/",
        "Zimbabwe Power Company": "https://www.zpc.co.zw/",
        "City of Harare Water": "https://www.hararecity.co.zw/water",

        # Solar - Installation and products
        "Zimbabwe Energy Regulatory Authority - Solar": "https://www.zera.co.zw/renewable-energy/solar/",
        "Zimbabwe Electricity Supply Authority Solar": "https://www.zesa.co.zw/renewable-energy/solar/",
        "Sunshine Solar": "https://www.sunshinesolar.co.zw/",
        "EcoSolar Zimbabwe": "https://www.ecosolar.co.zw/",

        # Mobility - Vehicles and transport
        "Auto Zimbabwe - Car Dealerships": "https://www.autozimbabwe.com/",
        "Zimbabwe Revenue Authority - Vehicle Registration": "https://www.zimra.co.zw/vehicle-registration/",
        "Driving Schools Association of Zimbabwe": "https://www.dsaz.co.zw/",
        "Zimbabwe Bus Services": "https://www.zimbabwebus.com/",

        # Hotels - Accommodation
        "Meikles Hotel": "https://www.meikles.com/",
        "Rainbow Towers Hotel": "https://www.rainbowtowers.co.zw/",
        "Victoria Falls Hotel": "https://www.victoriafallshotel.com/",
        "Monomotapa Hotel": "https://www.meikles.com/monomotapa-hotel"
    }

    # Get current sources
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/sources/', timeout=10) as response:
        sources = json.loads(response.read().decode())

    print(f"Found {len(sources)} sources, checking for updates...")

    updated_count = 0
    for source in sources:
        source_name = source['name']
        if source_name in comprehensive_updates:
            new_url = comprehensive_updates[source_name]
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
                            print(f"✅ Updated {source_name}")
                            print(f"   {source['base_url']} → {new_url}")
                            updated_count += 1
                        else:
                            print(f"❌ Failed to update {source_name}")
                except Exception as e:
                    print(f"❌ Error updating {source_name}: {e}")
            else:
                print(f"ℹ️  {source_name} already correct")

    print(f"\n✅ Updated {updated_count} source URLs")
    print("\n📋 NEXT STEPS:")
    print("1. Run: python test_url_fixes.py")
    print("2. Run: python validate_extraction.py")
    print("3. Pick first category to focus on (recommend: banking)")

if __name__ == "__main__":
    expand_url_corrections()