import sqlite3
conn = sqlite3.connect('scraper_hub.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM sources')
print(f'Total Sources: {cursor.fetchone()[0]}')
cursor.execute('SELECT category, COUNT(*) FROM sources GROUP BY category')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')
conn.close()
