import sqlite3
conn = sqlite3.connect('scraper_hub.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT source_url, COUNT(*) 
    FROM extracted_records 
    WHERE captured_at > datetime('now', '-1 hour')
    GROUP BY source_url
''')
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} records")
conn.close()
