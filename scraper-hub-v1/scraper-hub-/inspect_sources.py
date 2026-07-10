import sqlite3

DB_PATH = 'scraper_hub.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
for url in [
    'https://telecel.co.zw/value-added-services/',
    'https://telecel.co.zw/value-added-services',
]:
    cur.execute('SELECT id, url, name, category FROM sources WHERE url LIKE ?', (url + '%',))
    rows = cur.fetchall()
    print('SOURCE rows for', url)
    for row in rows:
        print(row)
    print('---')
    cur.execute('SELECT id, source_url, title FROM extracted_records WHERE source_url LIKE ?', (url + '%',))
    rows = cur.fetchall()
    print('EXTRACTED rows for', url, 'count=', len(rows))
    for row in rows[:10]:
        print(row)
    print('===')
conn.close()
