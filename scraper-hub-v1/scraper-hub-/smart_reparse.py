"""
Smart reparse script: re-processes all snapshots with improved extractors.
- First cleans noise records (price=0, suspicious titles)
- Then re-extracts with the improved extractor suite
"""
import sys
import os
import logging

# Force UTF-8 output on Windows to avoid charmap errors
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

# Suppress SQLAlchemy verbose logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

from app.db.session import SessionLocal
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.source import Source
from app.db.models.source_page import SourcePage
from app.services.extractor import ExtractorService


NOISE_TITLES = [
    'personalise', 'join today', 'sign in', 'back to', 'login', 'forgot password',
    'cookies', 'privacy policy', 'terms & conditions', 'contact us',
    'about us', 'search results', 'loading...', 'follow us', 'get in touch'
]

# Priority: Zimbabwe-specific sources with known good content
PRIORITY_CATEGORIES = ['banking', 'telecom', 'education', 'insurance', 'transport', 'hotels', 'utilities', 'solar']

def clean_noise_records(db):
    """Remove records with suspicious $0 prices and noise titles."""
    noise_deleted = 0
    records = db.query(ExtractedRecord).filter(
        (ExtractedRecord.price_value == 0) | (ExtractedRecord.price_value == None)
    ).all()
    
    for r in records:
        title_lower = r.title.lower() if r.title else ''
        if any(noise in title_lower for noise in NOISE_TITLES):
            db.delete(r)
            noise_deleted += 1
    
    db.commit()
    print(f"Cleaned {noise_deleted} noise records (price=0 + suspicious title)")
    return noise_deleted

def reparse_all():
    db = SessionLocal()
    extractor_service = ExtractorService(db)
    
    # Step 1: Clean noise records
    print("=== Step 1: Cleaning noise records ===")
    clean_noise_records(db)
    
    # Step 2: Get snapshots grouped by category priority
    print("\n=== Step 2: Reparsing snapshots ===")
    
    all_snapshots = db.query(RawSnapshot).filter(
        RawSnapshot.content != None,
        RawSnapshot.content != ''
    ).order_by(RawSnapshot.id.asc()).all()
    
    print(f"Total snapshots to reparse: {len(all_snapshots)}")
    
    stats = {}
    for i, snapshot in enumerate(all_snapshots):
        try:
            # Get category
            cat = "unknown"
            if snapshot.source_page_id:
                source = db.query(Source).join(SourcePage).filter(
                    SourcePage.id == snapshot.source_page_id
                ).first()
                if source:
                    cat = source.category

            # Skip tiny/empty content
            if not snapshot.content or len(snapshot.content) < 2000:
                continue
            
            # Clear existing records
            deleted = db.query(ExtractedRecord).filter(
                ExtractedRecord.snapshot_id == snapshot.id
            ).delete()
            db.commit()
            
            # Re-extract
            records = extractor_service.extract_from_snapshot(snapshot)
            count = len(records)
            
            if count > 0:
                print(f"  [{i+1}/{len(all_snapshots)}] snap={snapshot.id} ({cat}) | {snapshot.url[:55]} -> {count} records")

            
            stats[cat] = stats.get(cat, 0) + count
            
        except Exception as e:
            print(f"  ERROR snap={snapshot.id}: {e}")
            db.rollback()
    
    db.close()
    
    print("\n=== Reparse Complete ===")
    print("Records extracted by category:")
    total = 0
    for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
        total += count
    print(f"  TOTAL: {total}")

if __name__ == "__main__":
    reparse_all()
