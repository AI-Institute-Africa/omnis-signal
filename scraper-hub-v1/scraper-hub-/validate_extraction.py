import urllib.request
import json

def validate_current_extraction():
    """Validate what data is currently being extracted vs expected categories"""

    print("🔍 SCRAPER VALIDATION REPORT")
    print("=" * 60)
    print("Checking if extracted data matches category expectations...\n")

    # Get current records (increase limit to get all)
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/records/?limit=1000', timeout=10) as response:
        records = json.loads(response.read().decode())

    # Category expectations based on user specifications
    category_expectations = {
        'banking': {
            'description': 'Banks, accounts, loans, fees, digital features',
            'expected_content': ['accounts', 'loans', 'cards', 'fees', 'savings', 'mortgages', 'digital banking'],
            'expected_prices': True
        },
        'telecom': {
            'description': 'Providers, data bundles, voice rates, coverage metrics',
            'expected_content': ['data bundles', 'voice rates', 'plans', 'broadband', 'mobile', 'coverage'],
            'expected_prices': True
        },
        'schools': {
            'description': 'Educational institutions, tuition, facilities, pass rates',
            'expected_content': ['tuition', 'fees', 'facilities', 'pass rates', 'admission', 'examinations'],
            'expected_prices': True
        },
        'universities': {
            'description': 'Higher education institutions, programs, fees',
            'expected_content': ['tuition', 'programs', 'courses', 'fees', 'admission', 'degrees'],
            'expected_prices': True
        },
        'insurance': {
            'description': 'Providers, policies (motor, medical, life, property)',
            'expected_content': ['motor insurance', 'medical', 'life insurance', 'property', 'policies', 'premiums'],
            'expected_prices': True
        },
        'utilities': {
            'description': 'Utility providers and services',
            'expected_content': ['electricity', 'water', 'gas', 'internet', 'billing', 'rates'],
            'expected_prices': True
        },
        'solar': {
            'description': 'Solar energy providers and installations',
            'expected_content': ['solar panels', 'installation', 'solar energy', 'renewable', 'pricing'],
            'expected_prices': True
        },
        'mobility': {
            'description': 'Car dealerships, vehicles, driving schools, bus routes',
            'expected_content': ['cars', 'vehicles', 'dealerships', 'driving schools', 'bus routes', 'transport'],
            'expected_prices': True
        },
        'transport': {
            'description': 'Transportation services',
            'expected_content': ['transport', 'services', 'routes', 'schedules', 'fares'],
            'expected_prices': True
        },
        'hotels': {
            'description': 'Accommodation providers and stays',
            'expected_content': ['rooms', 'accommodation', 'hotels', 'rates', 'booking', 'stays'],
            'expected_prices': True
        }
    }

    # Group records by category
    records_by_category = {}
    for record in records:
        cat = record.get('category', 'unknown')
        if cat not in records_by_category:
            records_by_category[cat] = []
        records_by_category[cat].append(record)

    # Analyze each category
    for category, expectation in category_expectations.items():
        print(f"🏷️  {category.upper()}")
        print(f"   Expected: {expectation['description']}")
        print(f"   Should contain: {', '.join(expectation['expected_content'])}")

        if category in records_by_category:
            cat_records = records_by_category[category]
            print(f"   ✅ Records found: {len(cat_records)}")

            # Check for pricing
            priced_records = [r for r in cat_records if (r.get('price_value', 0) or 0) > 0]
            print(f"   💰 Records with prices: {len(priced_records)}/{len(cat_records)}")

            # Sample records
            print("   📋 Sample records:")
            for i, record in enumerate(cat_records[:3]):
                title = record.get('title', 'N/A')[:60]
                price = record.get('price_value', 0) or 0
                entity = record.get('entity_name', 'Unknown')
                print(f"      {i+1}. {entity}: {title} (£{price:.2f})")

            if len(cat_records) > 3:
                print(f"      ... and {len(cat_records)-3} more")

            # Validation score
            has_prices = len(priced_records) > 0
            has_relevant_content = any(
                any(keyword.lower() in record.get('title', '').lower() or
                    keyword.lower() in (record.get('description') or '').lower()
                    for keyword in expectation['expected_content'])
                for record in cat_records[:10]  # Check first 10 records
            )

            if has_prices and has_relevant_content:
                print("   ✅ VALIDATION: Good - Has prices and relevant content")
            elif has_relevant_content:
                print("   ⚠️  VALIDATION: Partial - Has relevant content but missing prices")
            else:
                print("   ❌ VALIDATION: Poor - Missing relevant content and prices")

        else:
            print("   ❌ Records found: 0")
            print("   ❌ VALIDATION: No data extracted for this category")

        print()

    # Overall summary
    print("=" * 60)
    print("📊 OVERALL VALIDATION SUMMARY")
    print("=" * 60)

    categories_with_data = [cat for cat in category_expectations.keys() if cat in records_by_category]
    categories_with_prices = [
        cat for cat in categories_with_data
        if any(r.get('price_value', 0) or 0 > 0 for r in records_by_category[cat])
    ]

    print(f"Categories with data: {len(categories_with_data)}/10")
    print(f"Categories with prices: {len(categories_with_prices)}/10")
    print(f"Total records: {len(records)}")

    print(f"\n🔴 ISSUES IDENTIFIED:")
    print("   1. Extractors finding generic website text instead of product data")
    print("   2. Most records have £0.00 prices - no actual pricing extracted")
    print("   3. Content doesn't match category expectations (e.g., 'Back to my accounts')")
    print("   4. Need better targeting of product/service pages vs homepages")

    print(f"\n💡 RECOMMENDATIONS:")
    print("   1. Update source URLs to point to specific product/pricing pages")
    print("   2. Improve CSS selectors to target product cards and pricing tables")
    print("   3. Add better regex patterns for price extraction")
    print("   4. Consider category-specific extractors with custom logic")

if __name__ == "__main__":
    validate_current_extraction()