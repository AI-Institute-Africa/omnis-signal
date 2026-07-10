import sqlite3

conn = sqlite3.connect('scraper_hub.db')
c = conn.cursor()
queries = [
    "SELECT id,name,base_url FROM sources WHERE base_url LIKE '%econet.co.zw%';",
    "SELECT id,source_id,url,page_type,enabled FROM source_pages WHERE url LIKE '%econet.co.zw%';",
    "SELECT id,name,base_url FROM sources WHERE base_url LIKE '%netone.co.zw%';",
    "SELECT id,source_id,url,page_type,enabled FROM source_pages WHERE url LIKE '%netone.co.zw%';",
    "SELECT id,source_id,url,page_type,enabled FROM source_pages WHERE url LIKE '%zwg-bundles%';",
    "SELECT COUNT(*) FROM extracted_records WHERE source_url = 'https://www.netone.co.zw/zwg-bundles';",
    "SELECT COUNT(*) FROM extracted_records WHERE source_url = 'https://www.econet.co.zw/usd-data-bundles/';"
]
for q in queries:
    print('QUERY:', q)
    for row in c.execute(q).fetchall():
        print(row)
    print()
conn.close()
