import sqlite3
con = sqlite3.connect('scraper_hub.db')
cur = con.cursor()
print('sources schema:')
for row in cur.execute('PRAGMA table_info(sources)'):
    print(row)
print('---')
print('extracted_records schema:')
for row in cur.execute('PRAGMA table_info(extracted_records)'):
    print(row)
con.close()
