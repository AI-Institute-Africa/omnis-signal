import sqlite3

conn = sqlite3.connect('scraper_hub.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute(
    "SELECT id, entity_name, title, description, price_value, price_currency, billing_period, unit_value, unit_type, category, subcategory, source_url, captured_at, confidence_score "
    "FROM extracted_records WHERE source_url LIKE '%netone.co.zw/usd-bundles%' ORDER BY id DESC LIMIT 20"
)
rows = cur.fetchall()
print('ROWS', len(rows))
for r in rows:
    print(dict(r))
conn.close()
