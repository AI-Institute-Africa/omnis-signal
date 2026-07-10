import pandas as pd

# Load Zimbabwe data (CSV should be regenerated from DB for freshest results)
df = pd.read_csv('zimbabwe_telecom_intelligence.csv')

# normalize for flexible matching (handles variants like 'Econet', 'Econet Wireless', 'Netone', etc.)
df['provider_name_l'] = df['provider_name'].fillna('').str.lower()
df['source_url_l'] = df.get('source_url', '').fillna('').str.lower()

# provider keywords to match against provider_name or source_url
provider_patterns = {
    'Econet': 'econet',
    'NetOne': 'netone',
    'TelOne': 'telone',
    'Tagtel': 'tagtel',
    'Telecel': 'telecel'
}

# build combined mask for Zimbabwe providers of interest
mask = False
for pat in provider_patterns.values():
    mask = mask | df['provider_name_l'].str.contains(pat, na=False) | df['source_url_l'].str.contains(pat, na=False)

zw = df[mask]

print("\n" + "="*90)
print("🇿🇼 ZIMBABWE TELECOM MARKET INTELLIGENCE - FILTERED DATA")
print("="*90)

print(f"\n📊 TOTAL MATCHING: {len(zw)} Offerings (matching provider keywords: {', '.join(provider_patterns.values())})\n")

# Show data organized by provider keyword (best-effort grouping)
for display_name, pat in provider_patterns.items():
    prov_mask = zw['provider_name_l'].str.contains(pat, na=False) | zw['source_url_l'].str.contains(pat, na=False)
    prov_data = zw[prov_mask]
    if len(prov_data) > 0:
        print(f"\n{'='*90}")
        print(f"🇿🇼 {display_name.upper()} - {len(prov_data)} OFFERINGS")
        print(f"{'='*90}")
        for idx, row in prov_data.head(50).iterrows():
            price = row.get('price_usd', None)
            price_display = f"${price:8.2f}" if pd.notna(price) else "N/A"
            currency = row.get('currency', '') if pd.notna(row.get('currency', '')) else ''
            validity = row.get('validity', '') if pd.notna(row.get('validity', '')) else ''
            service = row.get('service_name', '')
            print(f"  • {service:40} | {price_display} {currency:3} | {validity}")

# Summary stats
print("\n\n" + "="*90)
print("SUMMARY STATISTICS:")
print("="*90)
print(f"  Total Matching Offerings: {len(zw)}")
print(f"  Distinct Provider Names Found: {zw['provider_name'].nunique()}")
cats = zw['service_category'].dropna().unique().tolist()
print(f"  Categories: {', '.join(cats) if cats else 'none found'}")
if zw['price_usd'].dropna().size:
    print(f"  Price Range: ${zw['price_usd'].min():.2f} - ${zw['price_usd'].max():.2f}")
else:
    print("  Price Range: none")
currs = zw['currency'].dropna().unique().tolist()
print(f"  Currencies: {', '.join(currs) if currs else 'none found'}")

print("\n" + "="*90)
print("Note: If you still don't see records, regenerate `zimbabwe_telecom_intelligence.csv` from the database so this view reflects the latest extracted records.")
print("="*90 + "\n")
