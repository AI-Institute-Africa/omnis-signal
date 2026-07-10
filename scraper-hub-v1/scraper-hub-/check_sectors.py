import sqlite3
conn = sqlite3.connect('scraper_hub.db')
cursor = conn.cursor()
cursor.execute("SELECT entity_name, title, category, price_value, price_currency FROM extracted_records WHERE category IN ('hotels', 'insurance') LIMIT 20")
for row in cursor.fetchall():
    print(row)
conn.close()
