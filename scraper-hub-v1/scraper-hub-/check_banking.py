import sqlite3
conn = sqlite3.connect('scraper_hub.db')
cursor = conn.cursor()
cursor.execute("SELECT entity_name, title, category, source_url FROM extracted_records WHERE category = 'banking' LIMIT 20")
for row in cursor.fetchall():
    print(row)
conn.close()
