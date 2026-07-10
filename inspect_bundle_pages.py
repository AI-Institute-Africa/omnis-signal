import sqlite3
import json
DB=r'c:\Users\USER 2\Downloads\scraper-hub-v1 (2)\\scraper-hub-v1\\scraper-hub-\\scraper_hub.db'
conn=sqlite3.connect(DB)
c=conn.cursor()
queries=[
    ('Econet USD','SELECT s.id,s.name,s.base_url,sp.id,sp.url,sp.page_type,sp.enabled,sp.schedule FROM sources s JOIN source_pages sp ON s.id=sp.source_id WHERE sp.url LIKE "%usd-data-bundles%" OR s.base_url LIKE "%econet.co.zw%";'),
    ('NetOne ZWG','SELECT s.id,s.name,s.base_url,sp.id,sp.url,sp.page_type,sp.enabled,sp.schedule FROM sources s JOIN source_pages sp ON s.id=sp.source_id WHERE sp.url LIKE "%zwg-bundles%" OR s.base_url LIKE "%netone.co.zw%";')
]
for label,q in queries:
    print('\nQUERY:',label)
    rows=c.execute(q).fetchall()
    if not rows:
        print('  none')
    else:
        for r in rows:
            print('  source_id=',r[0],'name=',r[1],'base_url=',r[2])
            print('    page_id=',r[3],'url=',r[4],'type=',r[5],'enabled=',r[6],'schedule=',r[7])
conn.close()
