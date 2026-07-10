from app.db.session import SessionLocal
from app.db.models.extracted_record import ExtractedRecord

db = SessionLocal()
recs = db.query(ExtractedRecord).order_by(ExtractedRecord.captured_at.desc()).limit(20).all()
print(f'Total in DB: {db.query(ExtractedRecord).count()}')
print('ID\tEntity\tCategory\tProduct\tPrice\tCurrency\tSource URL\tCaptured At')
for r in recs:
    price_val = r.price_value if r.price_value is not None else "-"
    print(f'{r.id}\t{r.entity_name}\t{r.category}\t{r.title}\t{price_val}\t{r.price_currency}\t{r.source_url}\t{r.captured_at}')
