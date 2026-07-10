import os
import json
from app.db.session import get_db_session
from app.db.models import RawSnapshot
from app.scraping.extractors.base import BaseExtractor
from app.scraping.schemas import ExtractionResponse

# Mock Extractor for testing
class TestExtractor(BaseExtractor):
    def extract(self): return []
    def get_entity_name(self): return "Econet"
    def get_category(self): return "telecom"

def test_taxonomy_extraction():
    # Sample Econet content
    sample_text = """
    Econet Wireless Zimbabwe Data Bundles:
    - Smart USD 1: 1GB Data, valid for 24 hours. Price $1.
    - Private WiFi 10GB: 10GB high speed data, monthly subscription. Price $20.
    - Voice: On-net calls at $0.15 per minute.
    """
    
    # Create a dummy snapshot
    snapshot = RawSnapshot(
        url="https://www.econet.co.zw/bundles",
        content=sample_text,
        content_type="text/html"
    )
    
    extractor = TestExtractor(snapshot, "telecom")
    
    print("Triggering Gemini extraction with new taxonomy...")
    extraction = extractor._extract_with_gemini(sample_text)
    
    print("\nExtraction Results:")
    print(json.dumps(extraction.model_dump(), indent=2))
    
    # Check if subcategories and normalization are present
    for product in extraction.products:
        print(f"Product: {product.name}")
        print(f"  Category: {product.category}")
        print(f"  Subcategory: {product.subcategory}")
        print(f"  Price: {product.price.price_value}")
        print(f"  Normalized: {product.price.normalized_value} {product.price.normalized_unit}")
        print(f"  Formula: {product.price.formula}")
        print(f"  Daily: {product.price.daily}")
        print(f"  Monthly: {product.price.monthly}")

if __name__ == "__main__":
    test_taxonomy_extraction()
