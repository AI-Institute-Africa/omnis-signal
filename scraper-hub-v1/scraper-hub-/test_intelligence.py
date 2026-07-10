import asyncio
from app.db.session import SessionLocal
from app.services.intelligence import IntelligenceService
from app.db.models import RawSnapshot, Organization
from app.services.extractor import ExtractorService

async def test_intelligence():
    db = SessionLocal()
    intel_service = IntelligenceService(db)
    extractor_service = ExtractorService(db)
    
    # 1. Find a snapshot from a known organization
    # Let's try to find one for Old Mutual or something similar
    snapshot = db.query(RawSnapshot).filter(RawSnapshot.url.contains("stewardbank")).first()
    
    if not snapshot:
        # Fallback to any snapshot if stewardbank not found
        snapshot = db.query(RawSnapshot).order_by(RawSnapshot.created_at.desc()).first()
        
    if not snapshot:
        print("No snapshots found in DB.")
        return

    print(f"Testing Intelligence for Snapshot ID: {snapshot.id}")
    print(f"URL: {snapshot.url}")
    
    # Get the appropriate extractor
    extractor = extractor_service._get_extractor(snapshot, category_hint="banking")
    
    print(f"Using Extractor: {extractor.__class__.__name__}")
    print(f"Entity Name Detected: {extractor.get_entity_name()}")
    
    # Check if Org exists
    org = db.query(Organization).filter(Organization.name.ilike(f"%{extractor.get_entity_name()}%")).first()
    if org:
        print(f"Found Organization: {org.name} (ID: {org.id})")
    else:
        print(f"No Organization found for {extractor.get_entity_name()}")
        # Create a dummy one for testing if needed
        # org = Organization(name=extractor.get_entity_name(), slug="test-org", category="test")
        # db.add(org)
        # db.commit()
    
    print("\nRunning AI Intelligence Engine...")
    try:
        # Note: This will actually call Gemini if API Key is valid
        # If it fails due to API Key, it will catch the error
        extraction = intel_service.process_snapshot_with_ai(snapshot, extractor)
        print(f"Success! Extracted {len(extraction.products)} products and {len(extraction.services)} services.")
        
        # Check for change events
        from app.db.models import OrgChangeEvent
        events = db.query(OrgChangeEvent).filter(OrgChangeEvent.source_url == snapshot.url).all()
        print(f"Created {len(events)} Org Change Events.")
        for e in events:
            print(f"Event: {e.title} | {e.description}")
            
    except Exception as e:
        print(f"AI Extraction failed: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_intelligence())
