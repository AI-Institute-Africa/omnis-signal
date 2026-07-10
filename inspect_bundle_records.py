import sqlite3
DB=r'c:\Users\USER 2\Downloads\scraper-hub-v1 (2)\\scraper-hub-v1\\scraper-hub-\\scraper_hub.db'
conn=sqlite3.connect(DB)
c=conn.cursor()
patterns=[
    ('Econet USD','%econet.co.zw/usd-data-bundles%'),
    ('NetOne ZWG','%netone.co.zw/zwg-bundles%'),
    ('Econet ZWG','%econet.co.zw/zwg-data-bundles%'),
    ('NetOne USD','%netone.co.zw/usd-bundles%'),
    ('Telecel VAS','%telecel.co.zw/value-added-services%')
]
for label,pat in patterns:
    print('\n===', label, '===')
    rows=c.execute('SELECT source_url, COUNT(*) FROM extracted_records WHERE source_url LIKE ? GROUP BY source_url', (pat,)).fetchall()
    if not rows:
        print('  no extracted_records match')
        continue
    for source_url,count in rows:
        print('  source_url=',source_url,'count=',count)
    print('  sample rows:')
    rows=c.execute('SELECT title, item_name, price_value, price_currency, billing_period, source_url FROM extracted_records WHERE source_url LIKE ? ORDER BY id DESC LIMIT 5', (pat,)).fetchall()
    for r in rows:
        print('   ',r)
conn.close()
