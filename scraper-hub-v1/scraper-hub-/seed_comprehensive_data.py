from datetime import datetime
from app.db.session import SessionLocal
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.source import Source
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.source_page import SourcePage

def seed_all_categories():
    db = SessionLocal()
    
    manual_source = db.query(Source).filter(Source.name == "Market Intelligence Manual").first()
    if not manual_source:
        manual_source = Source(name="Market Intelligence Manual", category="general", base_url="https://internal.local")
        db.add(manual_source)
        db.commit()
        db.refresh(manual_source)
    
    manual_page = db.query(SourcePage).filter(SourcePage.source_id == manual_source.id).first()
    if not manual_page:
        manual_page = SourcePage(source_id=manual_source.id, url="https://internal.local", page_type="manual")
        db.add(manual_page)
        db.commit()
        db.refresh(manual_page)

    manual_snapshot = RawSnapshot(
        source_page_id=manual_page.id,
        url="https://internal.local",
        content="Manual Comprehensive Entry",
        content_type="text/plain"
    )
    db.add(manual_snapshot)
    db.commit()
    db.refresh(manual_snapshot)

    snapshot_id = manual_snapshot.id
    records = []
    now = datetime.utcnow()

    # 1. BANKING
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="CBZ Bank", category="banking", subcategory="account_fees", title="Gold Account Monthly Fee", description="Monthly maintenance fee", price_value=5.00, price_currency="USD", billing_period="month", source_url="https://cbz.co.zw", captured_at=now, confidence_score=0.95),
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Stanbic Bank", category="banking", subcategory="loans", title="Personal Loan Interest", description="Annual interest rate for personal loans", price_value=12.0, price_currency="%", billing_period="year", source_url="https://stanbicbank.co.zw", captured_at=now, confidence_score=0.9)
    ])

    # 2. TELECOM
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Econet Wireless", category="telecom", subcategory="data_bundles", title="10GB Monthly Data Bundle", description="30-day data bundle", price_value=15.00, price_currency="USD", billing_period="month", source_url="https://econet.co.zw", captured_at=now, confidence_score=0.98),
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="NetOne", category="telecom", subcategory="voice_rates", title="On-net Voice Call", description="Per minute billing", price_value=0.08, price_currency="USD", billing_period="minute", source_url="https://netone.co.zw", captured_at=now, confidence_score=0.95)
    ])

    # 3. SCHOOLS
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="St. George's College", category="schools", subcategory="tuition", title="Form 1 Termly Fees", description="Tuition fee per term", price_value=2500.00, price_currency="USD", billing_period="term", source_url="https://stgeorges.co.zw", captured_at=now, confidence_score=0.9)
    ])

    # 4. UNIVERSITIES
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="University of Zimbabwe", category="universities", subcategory="tuition", title="BSc Computer Science", description="Semester tuition fee", price_value=1200.00, price_currency="USD", billing_period="semester", source_url="https://uz.ac.zw", captured_at=now, confidence_score=0.95)
    ])

    # 5. INSURANCE
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Old Mutual", category="insurance", subcategory="life_insurance", title="Comprehensive Life Cover", description="Monthly premium", price_value=25.00, price_currency="USD", billing_period="month", source_url="https://oldmutual.co.zw", captured_at=now, confidence_score=0.9),
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Zimnat", category="insurance", subcategory="motor_insurance", title="Full Third Party Motor", description="Annual premium for light motor vehicles", price_value=120.00, price_currency="USD", billing_period="year", source_url="https://zimnat.co.zw", captured_at=now, confidence_score=0.92)
    ])

    # 6. UTILITIES
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="ZETDC (ZESA)", category="utilities", subcategory="electricity", title="Residential Standard Tariff", description="Cost per kWh", price_value=0.10, price_currency="USD", billing_period="unit", source_url="https://zetdc.co.zw", captured_at=now, confidence_score=0.98),
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Harare City Council", category="utilities", subcategory="water", title="Domestic Water (0-10m3)", description="Basic water supply tier", price_value=0.80, price_currency="USD", billing_period="m3", source_url="https://hararecity.co.zw", captured_at=now, confidence_score=0.85)
    ])

    # 7. SOLAR
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Green Solar Zimbabwe", category="solar", subcategory="equipment", title="5kW Solar System Install", description="Full home installation", price_value=3500.00, price_currency="USD", billing_period="one-off", source_url="https://greensolar.co.zw", captured_at=now, confidence_score=0.9)
    ])

    # 8. MOBILITY
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="CFAO Motors", category="mobility", subcategory="vehicles", title="Toyota Hilux Double Cab", description="New vehicle purchase price", price_value=45000.00, price_currency="USD", billing_period="one-off", source_url="https://cfaomotors.co.zw", captured_at=now, confidence_score=0.88)
    ])

    # 9. TRANSPORT
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="ZUPCO", category="transport", subcategory="bus_fare", title="Urban Local Route", description="Single trip ticket", price_value=0.50, price_currency="USD", billing_period="trip", source_url="https://zupco.co.zw", captured_at=now, confidence_score=0.95),
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Intercape", category="transport", subcategory="cross_border", title="Harare to Johannesburg", description="One way coach ticket", price_value=40.00, price_currency="USD", billing_period="trip", source_url="https://intercape.co.za", captured_at=now, confidence_score=0.9)
    ])

    # 10. HOTELS
    records.extend([
        ExtractedRecord(snapshot_id=snapshot_id, entity_name="Meikles Hotel", category="hotels", subcategory="accommodation", title="Standard Room", description="Per night stay", price_value=150.00, price_currency="USD", billing_period="night", source_url="https://meikles.com", captured_at=now, confidence_score=0.95)
    ])

    db.add_all(records)
    db.commit()
    db.close()
    print(f"Successfully seeded {len(records)} records across all 10 categories.")

if __name__ == "__main__":
    seed_all_categories()
