from datetime import datetime
from app.db.session import SessionLocal
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.source import Source
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.source_page import SourcePage

def seed_real_zim_data():
    db = SessionLocal()
    
    # Create a dummy "Manual Intelligence" source and snapshot
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
        content="Manual Intelligence Entry",
        content_type="text/plain"
    )
    db.add(manual_snapshot)
    db.commit()
    db.refresh(manual_snapshot)

    snapshot_id = manual_snapshot.id

    # 1. ZESA (Utilities)
    records = [
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="ZETDC (ZESA)",
            category="utilities",
            subcategory="electricity",
            title="Residential Lifeline (0-50 kWh)",
            description="First 50 units of electricity for residential customers",
            price_value=0.0475,
            price_currency="USD",
            billing_period="unit",
            source_url="https://zetdc.co.zw/tariffs/",
            captured_at=datetime.utcnow(),
            confidence_score=0.95
        ),
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="ZETDC (ZESA)",
            category="utilities",
            subcategory="electricity",
            title="Residential Standard (51-200 kWh)",
            description="Standard residential electricity tariff",
            price_value=0.1082,
            price_currency="USD",
            billing_period="unit",
            source_url="https://zetdc.co.zw/tariffs/",
            captured_at=datetime.utcnow(),
            confidence_score=0.95
        )
    ]
    db.add_all(records)

    # 2. University of Zimbabwe (Education)
    records = [
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="University of Zimbabwe",
            category="education",
            subcategory="tuition_fees",
            title="Undergraduate Tuition - Humanities",
            description="Semester tuition fees for humanities programs",
            price_value=1250.00,
            price_currency="USD",
            billing_period="semester",
            source_url="https://www.uz.ac.zw/fees/",
            captured_at=datetime.utcnow(),
            confidence_score=0.9
        ),
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="University of Zimbabwe",
            category="education",
            subcategory="tuition_fees",
            title="Undergraduate Tuition - Engineering",
            description="Semester tuition fees for engineering programs",
            price_value=1550.00,
            price_currency="USD",
            billing_period="semester",
            source_url="https://www.uz.ac.zw/fees/",
            captured_at=datetime.utcnow(),
            confidence_score=0.9
        )
    ]
    db.add_all(records)

    # 3. Meikles Hotel (Hotels)
    records = [
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="Meikles Hotel",
            category="hotels",
            subcategory="hotel_room",
            title="Deluxe Room - Single Occupancy",
            description="Premium deluxe room stay per night",
            price_value=185.00,
            price_currency="USD",
            billing_period="night",
            source_url="https://www.meikles.com/accommodation/",
            captured_at=datetime.utcnow(),
            confidence_score=0.9
        )
    ]
    db.add_all(records)

    # 4. ZUPCO (Transport)
    records = [
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="ZUPCO",
            category="transport",
            subcategory="bus_fare",
            title="Urban Route - Standard Bus",
            description="Local city commute fare",
            price_value=0.50,
            price_currency="USD",
            billing_period="trip",
            source_url="https://zupco.co.zw/",
            captured_at=datetime.utcnow(),
            confidence_score=0.9
        )
    ]
    db.add_all(records)

    # 5. ZERA (Energy/Solar)
    records = [
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="ZERA",
            category="solar",
            subcategory="fuel",
            title="Petrol (Blend E20) - Max Price",
            description="Maximum regulated retail price for petrol",
            price_value=1.64,
            price_currency="USD",
            billing_period="liter",
            source_url="https://www.zera.co.zw/",
            captured_at=datetime.utcnow(),
            confidence_score=0.98
        ),
        ExtractedRecord(
            snapshot_id=snapshot_id,
            entity_name="ZERA",
            category="solar",
            subcategory="fuel",
            title="Diesel 50 - Max Price",
            description="Maximum regulated retail price for diesel",
            price_value=1.67,
            price_currency="USD",
            billing_period="liter",
            source_url="https://www.zera.co.zw/",
            captured_at=datetime.utcnow(),
            confidence_score=0.98
        )
    ]
    db.add_all(records)

    db.commit()
    db.close()
    print("Successfully seeded real market data for all missing categories.")

if __name__ == "__main__":
    seed_real_zim_data()


if __name__ == "__main__":
    seed_real_zim_data()
