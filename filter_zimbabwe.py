import pandas as pd

# Load the data
df = pd.read_csv('zimbabwe_telecom_intelligence.csv')

# Filter for Zimbabwe providers only
zw_providers = ['Econet Wireless Zimbabwe', 'NetOne Cellular', 'TelOne', 'Tagtel', 'Telecel Zimbabwe']
zw_df = df[df['provider_name'].isin(zw_providers)]

# Display summary
print('='*70)
print('ZIMBABWE TELECOM DATA - VERIFIED')
print('='*70)
print(f'\nTotal Zimbabwe Records: {len(zw_df)}')
print(f'Providers: {zw_df["provider_name"].nunique()}')
print(f'Categories: {zw_df["service_category"].nunique()}\n')

print('BY PROVIDER:')
for provider, count in zw_df['provider_name'].value_counts().items():
    print(f'  ✅ {provider}: {count} offerings')

print('\nBY CATEGORY:')
for category, count in zw_df['service_category'].value_counts().items():
    print(f'  📁 {category}: {count} offerings')

print('\nSAMPLE DATA (First 10):')
sample = zw_df[['provider_name', 'service_name', 'price_usd', 'currency', 'validity']].head(10)
for idx, row in sample.iterrows():
    print(f"  {row['provider_name']:25} | {row['service_name']:30} | ${row['price_usd']:.2f} {row['currency']}")

# Export Zimbabwe-only data
zw_df.to_csv('zimbabwe_telecom_intelligence_FILTERED.csv', index=False)
zw_df.to_excel('zimbabwe_telecom_intelligence_FILTERED.xlsx', index=False)
print('\n✅ Created: zimbabwe_telecom_intelligence_FILTERED.csv')
print('✅ Created: zimbabwe_telecom_intelligence_FILTERED.xlsx')
