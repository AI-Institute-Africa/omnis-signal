import os
import sys
sys.path.append(os.getcwd())
from app.db.session import SessionLocal
from app.db.models.extracted_record import ExtractedRecord

urls = ['econet.co.zw', 'netone.co.zw', 'telecel.co.zw']

db = SessionLocal()
for url in urls:
    rows = db.query(ExtractedRecord.entity_name).filter(ExtractedRecord.source_url.ilike(f'%{url}%')).distinct().all()
    print(url, [r[0] for r in rows])
    print('---')
db.close()
