import urllib.request
import json
import time

COMPREHENSIVE_SOURCES = [
    # --- TELECOM ---
    {"name": "MTN Group", "category": "telecom", "market": "global", "base_url": "https://www.mtn.com/", "schedule": "0 * * * *"},
    {"name": "Vodacom South Africa", "category": "telecom", "market": "global", "base_url": "https://www.vodacom.co.za/", "schedule": "0 * * * *"},
    {"name": "Safaricom Kenya", "category": "telecom", "market": "global", "base_url": "https://www.safaricom.co.ke/", "schedule": "0 * * * *"},
    {"name": "Airtel Africa", "category": "telecom", "market": "global", "base_url": "https://www.airtel.africa/", "schedule": "0 * * * *"},
    {"name": "Verizon US", "category": "telecom", "market": "global", "base_url": "https://www.verizon.com/", "schedule": "0 * * * *"},
    {"name": "AT&T US", "category": "telecom", "market": "global", "base_url": "https://www.att.com/", "schedule": "0 * * * *"},
    {"name": "T-Mobile US", "category": "telecom", "market": "global", "base_url": "https://www.t-mobile.com/", "schedule": "0 * * * *"},

    # --- BANKING ---
    {"name": "Standard Bank", "category": "banking", "market": "global", "base_url": "https://www.standardbank.com/", "schedule": "0 * * * *"},
    {"name": "Absa Group", "category": "banking", "market": "global", "base_url": "https://www.absa.africa/", "schedule": "0 * * * *"},
    {"name": "Nedbank", "category": "banking", "market": "global", "base_url": "https://www.nedbank.co.za/", "schedule": "0 * * * *"},
    {"name": "HSBC Global", "category": "banking", "market": "global", "base_url": "https://www.hsbc.com/", "schedule": "0 * * * *"},
    {"name": "JPMorgan Chase", "category": "banking", "market": "global", "base_url": "https://www.jpmorganchase.com/", "schedule": "0 * * * *"},
    {"name": "Bank of America", "category": "banking", "market": "global", "base_url": "https://www.bankofamerica.com/", "schedule": "0 * * * *"},

    # --- INSURANCE ---
    {"name": "Sanlam", "category": "insurance", "market": "global", "base_url": "https://www.sanlam.com/", "schedule": "0 * * * *"},
    {"name": "Old Mutual South Africa", "category": "insurance", "market": "global", "base_url": "https://www.oldmutual.co.za/", "schedule": "0 * * * *"},
    {"name": "Allianz Global", "category": "insurance", "market": "global", "base_url": "https://www.allianz.com/", "schedule": "0 * * * *"},
    {"name": "AXA Group", "category": "insurance", "market": "global", "base_url": "https://www.axa.com/", "schedule": "0 * * * *"},
    {"name": "Prudential Financial", "category": "insurance", "market": "global", "base_url": "https://www.prudential.com/", "schedule": "0 * * * *"},

    # --- HOSPITALITY ---
    {"name": "Marriott International", "category": "hotels", "market": "global", "base_url": "https://www.marriott.com/", "schedule": "0 * * * *"},
    {"name": "Hilton Hotels", "category": "hotels", "market": "global", "base_url": "https://www.hilton.com/", "schedule": "0 * * * *"},
    {"name": "Accor Hotels", "category": "hotels", "market": "global", "base_url": "https://all.accor.com/", "schedule": "0 * * * *"},
    {"name": "Radisson Hotels", "category": "hotels", "market": "global", "base_url": "https://www.radissonhotels.com/", "schedule": "0 * * * *"},

    # --- EDUCATION ---
    {"name": "University of Cape Town", "category": "education", "market": "global", "base_url": "https://www.uct.ac.za/", "schedule": "0 * * * *"},
    {"name": "University of Nairobi", "category": "education", "market": "global", "base_url": "https://www.uonbi.ac.ke/", "schedule": "0 * * * *"},
    {"name": "Harvard University", "category": "education", "market": "global", "base_url": "https://www.harvard.edu/", "schedule": "0 * * * *"},
    {"name": "Oxford University", "category": "education", "market": "global", "base_url": "https://www.ox.ac.uk/", "schedule": "0 * * * *"},

    # --- TRANSPORT ---
    {"name": "Ethiopian Airlines", "category": "transport", "market": "global", "base_url": "https://www.ethiopianairlines.com/", "schedule": "0 * * * *"},
    {"name": "Kenya Airways", "category": "transport", "market": "global", "base_url": "https://www.kenya-airways.com/", "schedule": "0 * * * *"},
    {"name": "Emirates", "category": "transport", "market": "global", "base_url": "https://www.emirates.com/", "schedule": "0 * * * *"},
    {"name": "DHL Global", "category": "transport", "market": "global", "base_url": "https://www.dhl.com/", "schedule": "0 * * * *"},
    {"name": "FedEx", "category": "transport", "market": "global", "base_url": "https://www.fedex.com/", "schedule": "0 * * * *"},

]

print(f"=== Adding {len(COMPREHENSIVE_SOURCES)} Comprehensive Global & African Sources ===")

for source in COMPREHENSIVE_SOURCES:
    try:
        data = json.dumps(source).encode('utf-8')
        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/v1/sources/',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"[OK] Added: {source['name']} (Category: {source['category']})")
    except Exception as e:
        print(f"[FAIL] Failed to add {source['name']}: {e}")
    time.sleep(0.1) # Brief pause to be gentle

print("\n=== Seeding Complete ===")
