import sqlite3

con = sqlite3.connect('scraper_hub.db')
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM extracted_records WHERE source_url LIKE '%telecel%' OR source_url LIKE '%telecel.co.zw%'")
print(cur.fetchone()[0])
con.close()
