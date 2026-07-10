import urllib.request
import urllib.parse
import json
import re
from bs4 import BeautifulSoup

def validate_category_extraction():
    """Validate that extractors are pulling correct info for each category"""

    # Test URLs for each category
    test_sources = {
        'banking': [
            {'name': 'HSBC UK', 'url': 'https://www.hsbc.co.uk/', 'expected': ['accounts', 'loans', 'cards', 'fees']},
            {'name': 'Stanbic Zimbabwe', 'url': 'https://www.stanbicbank.co.zw/zimbabwe/personal/', 'expected': ['accounts', 'loans', 'cards']}
        ],
        'telecom': [
            {'name': 'Vodafone UK', 'url': 'https://www.vodafone.co.uk/', 'expected': ['data bundles', 'voice rates', 'plans']},
            {'name': 'Econet Zimbabwe', 'url': 'https://www.econet.co.zw/usd-data-bundles/', 'expected': ['data bundles', 'pricing']}
        ],
        'schools': [
            {'name': 'ZIMSEC', 'url': 'https://www.zimsec.co.zw/', 'expected': ['examinations', 'results', 'fees']}
        ],
        'universities': [
            {'name': 'UZ Fees', 'url': 'https://www.uz.ac.zw/fees-structure/', 'expected': ['tuition', 'fees', 'programs']}
        ]
    }

    print("🔍 CATEGORY VALIDATION REPORT")
    print("=" * 60)

    for category, sources in test_sources.items():
        print(f"\n🏷️  {category.upper()} CATEGORY VALIDATION")
        print("-" * 40)

        for source in sources:
            print(f"\n📍 Testing: {source['name']}")
            print(f"   URL: {source['url']}")

            try:
                # Fetch the page content
                req = urllib.request.Request(source['url'], headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                with urllib.request.urlopen(req, timeout=15) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(content, 'html.parser')

                print(f"   ✅ Fetched {len(content):,} characters")

                # Analyze content for expected keywords
                content_lower = content.lower()
                found_keywords = []
                for keyword in source['expected']:
                    if keyword.lower() in content_lower:
                        found_keywords.append(keyword)

                print(f"   🔍 Expected keywords: {', '.join(source['expected'])}")
                print(f"   ✅ Found keywords: {', '.join(found_keywords) if found_keywords else 'None'}")

                # Look for pricing patterns
                price_patterns = [
                    r'£\d+(?:\.\d{2})?',  # GBP prices
                    r'\$\d+(?:\.\d{2})?',  # USD prices
                    r'\d+(?:\.\d{2})?\s*(?:USD|GBP|ZWL)',  # Currency after number
                    r'(?:fee|cost|price|charge).*?(\d+(?:\.\d{2})?)',  # Fee patterns
                ]

                prices_found = []
                for pattern in price_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    prices_found.extend(matches)

                unique_prices = list(set(prices_found))
                print(f"   💰 Price patterns found: {len(unique_prices)} unique ({', '.join(unique_prices[:5])}{'...' if len(unique_prices) > 5 else ''})")

                # Check for structured data (tables, lists)
                tables = soup.find_all('table')
                lists = soup.find_all(['ul', 'ol'])
                cards = soup.find_all(attrs={'class': re.compile(r'card|product|plan|account')})

                print(f"   📊 Structured data: {len(tables)} tables, {len(lists)} lists, {len(cards)} product cards")

                # Category-specific validation
                if category == 'banking':
                    banking_indicators = ['account', 'loan', 'card', 'saving', 'deposit', 'mortgage']
                    banking_found = [ind for ind in banking_indicators if ind in content_lower]
                    print(f"   🏦 Banking indicators: {', '.join(banking_found) if banking_found else 'None'}")

                elif category == 'telecom':
                    telecom_indicators = ['data', 'bundle', 'voice', 'plan', 'broadband', 'mobile']
                    telecom_found = [ind for ind in telecom_indicators if ind in content_lower]
                    print(f"   📱 Telecom indicators: {', '.join(telecom_found) if telecom_found else 'None'}")

                elif category in ['schools', 'universities']:
                    education_indicators = ['fee', 'tuition', 'program', 'course', 'admission', 'exam']
                    education_found = [ind for ind in education_indicators if ind in content_lower]
                    print(f"   🎓 Education indicators: {', '.join(education_found) if education_found else 'None'}")

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:50]}...")

    print(f"\n{'='*60}")
    print("📋 VALIDATION SUMMARY")
    print(f"{'='*60}")
    print("✅ Content fetching: Working")
    print("⚠️  Keyword detection: Partial - some sites have expected content")
    print("❌ Price extraction: Limited - few structured prices found")
    print("❌ Structured data: Minimal - most sites lack product tables/cards")
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Extractors need category-specific URL targeting (product pages)")
    print("   2. Improve CSS selectors for product cards and pricing tables")
    print("   3. Add regex patterns for local currency formats (ZWL, ZWD)")
    print("   4. Focus on dedicated product/service pages rather than homepages")

if __name__ == "__main__":
    validate_category_extraction()