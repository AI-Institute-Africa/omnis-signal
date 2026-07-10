import sqlite3
con = sqlite3.connect('scraper_hub.db')
cur = con.cursor()
cur.execute('SELECT * FROM sources LIMIT 1')
row = cur.fetchone()
print('columns:', [d[0] for d in cur.description])
print('sample row:', row)
cur.execute("SELECT COUNT(*) FROM sources WHERE lower(name) LIKE '%telecel%' OR lower(category) LIKE '%telecel%' OR lower(base_url) LIKE '%telecel%'")
print('telecel count:', cur.fetchone()[0])
cur.execute("SELECT id, name, category, base_url FROM sources WHERE lower(name) LIKE '%telecel%' OR lower(category) LIKE '%telecel%' OR lower(base_url) LIKE '%telecel%'")
for r in cur.fetchall():
    print(r)
con.close()
