import urllib.request
import json
from datetime import datetime

# Define all Zimbabwe sources to add
ZIMBABWE_SOURCES = [
    # TELECOM (Zimbabwe)
    {
        "name": "Econet Wireless",
        "category": "telecom",
        "market": "local",
        "base_url": "https://www.econet.co.zw/",
        "schedule": "0 7 * * *"  # Daily at 7 AM
    },

    {
        "name": "Econet Data Bundles",
        "category": "telecom",
        "base_url": "https://www.econet.co.zw/usd-data-bundles/",
        "schedule": "0 7 * * *"
    },
    {
        "name": "Econet Voice Rates",
        "category": "telecom",
        "base_url": "https://www.econet.co.zw/voice/",
        "schedule": "0 7 * * *"
    },
    {
        "name": "NetOne Zimbabwe",
        "category": "telecom",
        "base_url": "https://www.netone.co.zw/",
        "schedule": "0 8 * * *"
    },
    {
        "name": "NetOne Data Bundles",
        "category": "telecom",
        "base_url": "https://www.netone.co.zw/data-bundles/",
        "schedule": "0 8 * * *"
    },
    {
        "name": "NetOne Voice Tariffs",
        "category": "telecom",
        "base_url": "https://www.netone.co.zw/voice-tariffs/",
        "schedule": "0 8 * * *"
    },
    {
        "name": "Telecel Zimbabwe",
        "category": "telecom",
        "base_url": "https://www.telecel.co.zw/",
        "schedule": "0 9 * * *"
    },
    {
        "name": "Telecel Data Plans",
        "category": "telecom",
        "base_url": "https://www.telecel.co.zw/data-plans/",
        "schedule": "0 9 * * *"
    },
    {
        "name": "Telecel Voice Plans",
        "category": "telecom",
        "base_url": "https://www.telecel.co.zw/voice-plans/",
        "schedule": "0 9 * * *"
    },
    {
        "name": "Telecel Value Added Services",
        "category": "telecom",
        "base_url": "https://www.telecel.co.zw/value-added-services/",
        "schedule": "0 9 * * *"
    },
    {
        "name": "TelOne Zimbabwe",
        "category": "telecom",
        "base_url": "https://www.telone.co.zw/",
        "schedule": "0 9 * * *"
    },
    {
        "name": "TelOne Data Bundles",
        "category": "telecom",
        "base_url": "https://www.telone.co.zw/personal/broadband/data-bundles",
        "schedule": "0 9 * * *"
    },
    {
        "name": "Liquid Intelligent Technologies",
        "category": "telecom",
        "base_url": "https://www.liquid.tech/zimbabwe",
        "schedule": "0 9 * * *"
    },
    {
        "name": "PowerTel Zimbabwe",
        "category": "telecom",
        "base_url": "https://www.powertel.co.zw/",
        "schedule": "0 9 * * *"
    },

    
    # BANKING (Zimbabwe)
    {
        "name": "CBZ Bank",
        "category": "banking",
        "base_url": "https://www.cbz.co.zw/",
        "schedule": "0 10 * * *"
    },
    {
        "name": "CBZ Personal Banking",
        "category": "banking",
        "base_url": "https://www.cbz.co.zw/personal-banking/",
        "schedule": "0 10 * * *"
    },
    {
        "name": "FBC Bank",
        "category": "banking",
        "base_url": "https://www.fbc.co.zw/",
        "schedule": "0 11 * * *"
    },
    {
        "name": "FBC Personal Banking",
        "category": "banking",
        "base_url": "https://www.fbc.co.zw/personal/",
        "schedule": "0 11 * * *"
    },
    {
        "name": "Stanbic Bank Zimbabwe",
        "category": "banking",
        "base_url": "https://www.stanbicbank.co.zw/",
        "schedule": "0 12 * * *"
    },
    {
        "name": "Stanbic Personal Banking",
        "category": "banking",
        "base_url": "https://www.stanbicbank.co.zw/zimbabwe/personal/",
        "schedule": "0 12 * * *"
    },
    {
        "name": "ZB Bank",
        "category": "banking",
        "base_url": "https://www.zb.co.zw/",
        "schedule": "0 13 * * *"
    },
    {
        "name": "ZB Personal Banking",
        "category": "banking",
        "base_url": "https://www.zb.co.zw/personal-banking/",
        "schedule": "0 13 * * *"
    },
    {
        "name": "NMB Bank",
        "category": "banking",
        "base_url": "https://www.nmbbank.co.zw/",
        "schedule": "0 14 * * *"
    },
    {
        "name": "NMB Personal Banking",
        "category": "banking",
        "base_url": "https://www.nmbbank.co.zw/personal/",
        "schedule": "0 14 * * *"
    },
    {
        "name": "Ecobank Zimbabwe",
        "category": "banking",
        "base_url": "https://www.ecobank.com/zw",
        "schedule": "0 15 * * *"
    },
    {
        "name": "Ecobank Personal Banking",
        "category": "banking",
        "base_url": "https://www.ecobank.com/zw/personal-banking",
        "schedule": "0 15 * * *"
    },
    
    # INSURANCE (Zimbabwe)
    {
        "name": "Old Mutual Zimbabwe",
        "category": "insurance",
        "base_url": "https://www.oldmutual.co.zw/",
        "schedule": "0 7 * * 1"  # Weekly Monday
    },
    {
        "name": "Old Mutual Personal",
        "category": "insurance",
        "base_url": "https://www.oldmutual.co.zw/personal/",
        "schedule": "0 7 * * 1"
    },
    {
        "name": "NICO General Insurance",
        "category": "insurance",
        "base_url": "https://www.nico.co.zw/",
        "schedule": "0 8 * * 1"
    },
    {
        "name": "NICO Products",
        "category": "insurance",
        "base_url": "https://www.nico.co.zw/products/",
        "schedule": "0 8 * * 1"
    },
    {
        "name": "Zimnat Insurance",
        "category": "insurance",
        "base_url": "https://www.zimnat.co.zw/",
        "schedule": "0 9 * * 1"
    },
    {
        "name": "Zimnat Products",
        "category": "insurance",
        "base_url": "https://www.zimnat.co.zw/products/",
        "schedule": "0 9 * * 1"
    },
    {
        "name": "Fidelity Life Assurance",
        "category": "insurance",
        "base_url": "https://www.fidelitylife.co.zw/",
        "schedule": "0 10 * * 1"
    },
    {
        "name": "Fidelity Products",
        "category": "insurance",
        "base_url": "https://www.fidelitylife.co.zw/products/",
        "schedule": "0 10 * * 1"
    },
    {
        "name": "Britam Zimbabwe",
        "category": "insurance",
        "base_url": "https://www.britam.com/zimbabwe",
        "schedule": "0 11 * * 1"
    },
    {
        "name": "Britam Personal",
        "category": "insurance",
        "base_url": "https://www.britam.com/zimbabwe/personal/",
        "schedule": "0 11 * * 1"
    },
    
    # HOTELS (Zimbabwe)
    {
        "name": "Meikles Hotel",
        "category": "hotels",
        "base_url": "https://www.meikles.com/",
        "schedule": "0 12 * * *"
    },
    {
        "name": "Rainbow Towers Hotel",
        "category": "hotels",
        "base_url": "https://www.rainbowtowers.co.zw/",
        "schedule": "0 13 * * *"
    },
    {
        "name": "Victoria Falls Hotel",
        "category": "hotels",
        "base_url": "https://www.victoriafallshotel.com/",
        "schedule": "0 14 * * *"
    },
    {
        "name": "Zimbabwe Hotels on Booking.com",
        "category": "hotels",
        "base_url": "https://www.booking.com/region/zimbabwe/",
        "schedule": "0 15 * * *"
    },
    
    # UNIVERSITIES (Zimbabwe)
    {
        "name": "University of Zimbabwe",
        "category": "education",
        "base_url": "https://www.uz.ac.zw/",
        "schedule": "0 7 * * 2"  # Weekly Tuesday
    },
    {
        "name": "University of Zimbabwe Fees",
        "category": "education",
        "base_url": "https://www.uz.ac.zw/fees/",
        "schedule": "0 7 * * 2"
    },
    {
        "name": "NUST Zimbabwe",
        "category": "education",
        "base_url": "https://www.nust.ac.zw/",
        "schedule": "0 8 * * 2"
    },
    {
        "name": "NUST Fees",
        "category": "education",
        "base_url": "https://www.nust.ac.zw/fees/",
        "schedule": "0 8 * * 2"
    },
    {
        "name": "Midlands State University",
        "category": "education",
        "base_url": "https://www.msu.ac.zw/",
        "schedule": "0 9 * * 2"
    },
    {
        "name": "MSU Fees",
        "category": "education",
        "base_url": "https://www.msu.ac.zw/fees/",
        "schedule": "0 9 * * 2"
    },
    {
        "name": "Great Zimbabwe University",
        "category": "education",
        "base_url": "https://www.gzu.ac.zw/",
        "schedule": "0 10 * * 2"
    },
    {
        "name": "GZU Fees",
        "category": "education",
        "base_url": "https://www.gzu.ac.zw/fees/",
        "schedule": "0 10 * * 2"
    },
    
    # UTILITIES (Zimbabwe)
    {
        "name": "ZESA (Electricity)",
        "category": "utilities",
        "base_url": "https://www.zesa.co.zw/",
        "schedule": "0 16 * * 3"  # Weekly Wednesday
    },
    {
        "name": "ZESA Tariffs",
        "category": "utilities",
        "base_url": "https://www.zesa.co.zw/tariffs/",
        "schedule": "0 16 * * 3"
    },
    {
        "name": "ZINWA (Water)",
        "category": "utilities",
        "base_url": "https://www.zinwa.co.zw/",
        "schedule": "0 17 * * 3"
    },
    {
        "name": "ZINWA Tariffs",
        "category": "utilities",
        "base_url": "https://www.zinwa.co.zw/tariffs/",
        "schedule": "0 17 * * 3"
    },
    
    # SOLAR (Zimbabwe)
    {
        "name": "ZERA (Zimbabwe Energy Authority)",
        "category": "energy",
        "base_url": "https://www.zera.co.zw/",
        "schedule": "0 11 * * 3"
    },
    {
        "name": "Sunshine Solar",
        "category": "energy",
        "base_url": "https://www.sunshinesolar.co.zw/",
        "schedule": "0 12 * * 3"
    },
    {
        "name": "EcoSolar Zimbabwe",
        "category": "energy",
        "base_url": "https://www.ecosolar.co.zw/",
        "schedule": "0 13 * * 3"
    },
    
    # TRANSPORT (Zimbabwe)
    {
        "name": "ZIMRA (Revenue Authority)",
        "category": "transport",
        "base_url": "https://www.zimra.co.zw/",
        "schedule": "0 18 * * 3"
    },
    {
        "name": "ZUPCO (Passenger Transport)",
        "category": "transport",
        "base_url": "https://www.zupco.co.zw/",
        "schedule": "0 19 * * 3"
    },
]

print("=== Adding Zimbabwe Sources ===")
print(f"Total sources to add: {len(ZIMBABWE_SOURCES)}")

for source in ZIMBABWE_SOURCES:
    try:
        # Create source via API
        import urllib.parse
        data = json.dumps(source).encode('utf-8')
        
        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/v1/sources/',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"SUCCESS Added: {source['name']} (ID: {result['id']}, Category: {source['category']})")
    except Exception as e:
        print(f"FAILED to add {source['name']}: {e}")


print(f"\n=== Summary ===")
print(f"Processing complete. Check server logs for details.")
print(f"Categories added:")
print(f"  - Telecom: 9 sources")
print(f"  - Banking: 10 sources")
print(f"  - Insurance: 10 sources")
print(f"  - Hotels: 4 sources")
print(f"  - Education: 8 sources")
print(f"  - Utilities: 4 sources")
print(f"  - Energy: 3 sources")
print(f"  - Transport: 2 sources")
print(f"  TOTAL: {len(ZIMBABWE_SOURCES)} sources")