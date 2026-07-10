import sqlite3

DB_PATH = 'scraper_hub.db'
URL = 'https://www.telecel.co.zw/value-added-services/'

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM extracted_records WHERE source_url LIKE ? OR source_url = ?",
        (URL + '%', URL)
    )
    count = cur.fetchone()[0]
    print('Telecel value-added-services record count:', count)

    cur.execute(
        "SELECT id, title, price_value, price_currency, source_url FROM extracted_records WHERE source_url LIKE ? OR source_url = ? LIMIT 10",
        (URL + '%', URL)
    )
    for row in cur.fetchall():
        print(row)

    cur.execute("SELECT id, name, base_url FROM sources WHERE base_url = ?", (URL,))
    print('source rows:')
    for row in cur.fetchall():
        print(row)

    cur.execute("SELECT id, source_id, url, page_type, enabled FROM source_pages WHERE url = ?", (URL,))
    print('source page rows:')
    for row in cur.fetchall():
        print(row)
