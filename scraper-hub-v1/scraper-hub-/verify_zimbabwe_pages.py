import os
import sys

sys.path.append(os.getcwd())
from app.db.session import SessionLocal
from app.db.models.source import Source
from app.db.models.source_page import SourcePage

urls = [
    'https://www.telone.co.zw/Products/Broadband',
    'https://www.telone.co.zw/products/details/service-tariffs-effective-5-august-2025',
    'https://africom.co.zw/product-category/data-services/',
    'https://www.liquidhome.co.zw/packages/',
    'https://www.dandemutande.co.zw/home-fibre/',
    'https://www.utande.co.zw/',
    'https://www.tagtel.co.zw/data-plans/',
    'https://www.zol.co.zw/',
]

db = SessionLocal()
for u in urls:
    p = db.query(SourcePage).filter(SourcePage.url == u).first()
    if p:
        s = db.query(Source).filter(Source.id == p.source_id).first()
        print(u, '->', s.name if s else 'unknown', 'page_id', p.id, 'enabled', p.enabled)
    else:
        print(u, '-> MISSING')

db.close()
