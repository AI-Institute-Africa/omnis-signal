import sqlite3

DB_PATH = 'scraper_hub.db'
URLS = [
    'https://www.econet.co.zw/zwg-data-bundles/',
    'https://www.netone.co.zw/usd-bundles',
    'https://telecel.co.zw/value-added-services/',
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
for url in URLS:
    cur.execute('SELECT COUNT(*) FROM extracted_records WHERE source_url LIKE ?', (url + '%',))
    count = cur.fetchone()[0]
    print(url, count)
    if count > 0:
        cur.execute('SELECT id, title, price_value, source_url FROM extracted_records WHERE source_url LIKE ? LIMIT 5', (url + '%',))
        for row in cur.fetchall():
            print(row)
        print('---')
conn.close()
