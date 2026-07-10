import sqlite3
DB=r'c:\Users\USER 2\Downloads\scraper-hub-v1 (2)\\scraper-hub-v1\\scraper-hub-\\scraper_hub.db'
conn=sqlite3.connect(DB)
c=conn.cursor()
patterns=[
    ('Econet ZWG','%zwg-data-bundles%','https://www.econet.co.zw/zwg-data-bundles/'),
    ('NetOne USD','%usd-bundles%','https://www.netone.co.zw/usd-bundles'),
    ('Telecel VAS','%value-added-services%','https://telecel.co.zw/value-added-services/')
]
for label,like_pat,url in patterns:
    print('\nCHECK:',label)
    q1='SELECT id,source_id,url,page_type,enabled FROM source_pages WHERE url LIKE ? OR url=?'
    rows=c.execute(q1,(like_pat,url)).fetchall()
    if not rows:
        print('  none')
    else:
        for r in rows:
            print('  page_id=',r[0],'source_id=',r[1],'url=',r[2],'type=',r[3],'enabled=',r[4])

# quick counts in extracted_records for each source_url
for label,like_pat,url in patterns:
    print('\nCOUNT for',label)
    q2='SELECT count(*) FROM extracted_records WHERE source_url LIKE ? OR source_url=?'
    try:
        c2=c.execute(q2,(like_pat,url)).fetchone()
        print(' ', c2[0])
    except Exception as e:
        print('  query failed:', e)

conn.close()
