import os
import sys

sys.path.append(os.getcwd())
from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage
from app.db.models.extracted_record import ExtractedRecord

names = ['Econet', 'NetOne', 'Telecel']
urls = ['econet.co.zw', 'netone.co.zw', 'telecel.co.zw']

db = SessionLocal()
print('--- SOURCES ---')
for name in names:
    rows = db.query(Source).filter(Source.name.ilike(f'%{name}%')).all()
    print(f'{name} sources: {len(rows)}')
    for r in rows:
        print('  ', r.id, r.name, r.base_url, r.category, r.market, r.schedule)

print('\n--- SOURCE PAGES ---')
for url in urls:
    rows = db.query(SourcePage).filter(SourcePage.url.ilike(f'%{url}%')).all()
    print(f'{url} pages: {len(rows)}')
    for r in rows:
        print('  ', r.id, r.source_id, r.url, r.page_type, r.enabled, r.schedule)

print('\n--- EXTRACTED RECORD COUNTS ---')
for url in urls:
    count = db.query(ExtractedRecord).filter(ExtractedRecord.source_url.ilike(f'%{url}%')).count()
    print(url, count)

print('\n--- UNIQUE SOURCE_URLS ---')
for url in urls:
    rows = db.query(ExtractedRecord.source_url).filter(ExtractedRecord.source_url.ilike(f'%{url}%')).distinct().all()
    print(url, [x[0] for x in rows])

db.close()
