import sqlite3
conn = sqlite3.connect('scraper_hub.db')
cursor = conn.cursor()
cursor.execute("SELECT name, category, base_url FROM sources WHERE name LIKE '%EE%'")
print(cursor.fetchall())
conn.close()
