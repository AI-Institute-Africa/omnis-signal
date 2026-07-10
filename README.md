# Zimbabwe Telecom Market Intelligence Scraper

A comprehensive Python-based scraper for collecting telecom market intelligence from Zimbabwe's major telecommunications operators and ISPs.

## 📊 Overview

This scraper systematically collects, normalizes, and exports pricing, bundles, tariffs, and service data from Zimbabwe's telecom providers including:

- **Econet Wireless Zimbabwe** (MNO)
- **NetOne Cellular** (MNO)
- **Telecel Zimbabwe** (MNO)
- **TelOne** (Fixed Telecom/ISP)
- **Tagtel** (MVNO)
- **Liquid Home Zimbabwe** (Fibre ISP)
- **Africom** (Enterprise ISP)
- **ZOL Zimbabwe** (ISP)
- **Dandemutande** (ISP)
- **Utande** (Data Centre/ISP)

## 📦 What's Included

### Files

1. **advanced_telecom_scraper.py** - Main scraper with complete provider coverage
2. **telecom_scraper.py** - Basic scraper template
3. **SCHEMA.md** - Complete data schema documentation
4. **requirements.txt** - Python dependencies
5. **README.md** - This file

### Generated Outputs

- **zimbabwe_telecom_intelligence.csv** - CSV format (Excel-compatible)
- **zimbabwe_telecom_intelligence.json** - JSON format (API-ready)
- **zimbabwe_telecom_intelligence.xlsx** - Excel spreadsheet with formatting

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the Scraper

```bash
python advanced_telecom_scraper.py
```

This will:
1. Collect data from all configured providers
2. Normalize prices (USD and local currency)
3. Export to CSV, JSON, and Excel formats
4. Display collection summary

## 📋 Data Schema

The scraper collects 44 fields per service offering:

### Core Fields
- `provider_name` - Telecom company name
- `provider_type` - MNO, ISP, MVNO, etc.
- `service_category` - voice_bundle, data_bundle, broadband_plan, etc.
- `service_name` - Product/bundle name
- `unit_type` - GB, MB, Minutes, SMS Count, Mbps, etc.
- `price_usd` - Normalized USD price
- `price_local` - Local currency price (ZWG, ZWD, etc.)
- `billing_period` - Daily, Weekly, Monthly, etc.
- `validity` - Service validity period

### Extended Fields
- `peak_data_gb` / `off_peak_data_gb` - Data breakdown
- `included_features` - Feature list (JSON)
- `confidence_score` - Data reliability (60-100%)
- `source_url` - Where data was scraped
- `activation_method` - How to activate (USSD, Web, App, etc.)
- `promotion_code` - USSD codes, promo codes
- `market_segment` - Target customer (Consumer, SME, Enterprise)

See **SCHEMA.md** for complete field definitions.

## 📊 Current Coverage

### Collected Data
- **34+ service offerings** from initial providers
- **5 major providers** fully configured
- **Service categories**:
  - 15 broadband plans
  - 5 data bundles
  - 6 SMS bundles
  - 8 social media bundles
  - More coming...

### Missing Data Identified
The scraper framework identifies these missing fields that need to be added:

1. **Provider Contact Information**
   - Email addresses
   - Phone numbers
   - Support channels

2. **Service Details**
   - Detailed descriptions
   - USSD activation codes
   - Auto-renewal status
   - Data rollover policies

3. **Advanced Features**
   - International roaming
   - Promo validity dates
   - Competitive analysis
   - Customer reviews

4. **Technical Information**
   - Speed specifications (Mbps)
   - Coverage areas
   - Device compatibility
   - API documentation

## 🔄 Architecture

### Class Hierarchy

```
ScraperBase (ABC)
├── EconetScraper
├── NetOneScraper
├── TelecelScraper
├── TelOneScraper
├── TagtelScraper
└── [Expandable for other providers]

MarketIntelligenceCollector
└── Orchestrates all scrapers
    └── Exports to CSV, JSON, Excel
```

### Service Offering Data Model

```python
@dataclass
class ServiceOffering:
    provider_name: str
    provider_type: str
    service_category: str
    service_name: str
    unit_type: str
    # ... 40+ additional fields
```

## 🛠️ Extension Guide

### Add a New Provider

```python
class NewProviderScraper(ScraperBase):
    """Scraper for New Provider"""
    
    def __init__(self):
        super().__init__('Company Name', 'MNO', 'https://website.com')
        self.provider_email = 'support@provider.com'
        self.provider_phone = '+263 xxx xxxx'
    
    def scrape(self) -> List[ServiceOffering]:
        logger.info("Scraping New Provider...")
        
        self.add_offering(
            service_category='data_bundle',
            service_name='Cool Bundle',
            unit_type='GB',
            unit_value=10.0,
            price_usd=5.99,
            # ... other fields
        )
        
        return self.offerings
```

Then register in `MarketIntelligenceCollector`:

```python
self.scrapers = [
    EconetScraper(),
    NetOneScraper(),
    NewProviderScraper(),  # Add here
    # ...
]
```

## 🌐 Advanced Features

### JavaScript-Rendered Content

For sites like Telecel that use JavaScript:

```python
# Uses Selenium WebDriver (install: pip install selenium)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# In scraper:
driver = webdriver.Chrome(options=options)
driver.get(url)
soup = BeautifulSoup(driver.page_source, 'html.parser')
```

### Currency Normalization

```python
# Automatic USD conversion
if currency == 'ZWG':
    price_usd = price_local / exchange_rate  # Use live rate
```

### Data Validation

```python
# Confidence scoring based on source
if source_type == 'official_website':
    confidence_score = 95
elif source_type == 'news_article':
    confidence_score = 70
```

## 📈 Usage Examples

### Load Data in Python

```python
import pandas as pd
import json

# From CSV
df = pd.read_csv('zimbabwe_telecom_intelligence.csv')

# Filter by provider
econet_data = df[df['provider_name'] == 'Econet Wireless Zimbabwe']

# Get all data bundles
data_bundles = df[df['service_category'] == 'data_bundle']

# Find cheapest 1GB bundle
one_gb = df[df['unit_value'] == 1.0].nsmallest(1, 'price_usd')
```

### Use JSON API

```bash
# Load in any application
curl -s file:///path/to/zimbabwe_telecom_intelligence.json | jq '.[] | select(.provider_name=="Econet")'
```

### Excel Analysis

```
1. Open zimbabwe_telecom_intelligence.xlsx
2. Data → Filter → Apply to find bundles by:
   - Price range
   - Provider
   - Service category
   - Validity period
```

## 🔍 Data Quality

### Quality Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Records | 34 | 500+ |
| Providers | 5 | 10 |
| Fields Populated | 24/44 | 44/44 |
| USD Normalization | 100% | 100% |
| Confidence Avg | 77% | 85%+ |

### Quality Checklist

- [x] Price normalization (USD)
- [x] Data categorization
- [x] URL source tracking
- [x] Timestamp metadata
- [ ] Contact information
- [ ] Service descriptions (50% complete)
- [ ] Coverage areas
- [ ] Customer reviews
- [ ] Historical pricing

## 🔐 Data Privacy & Terms

- **Terms**: Scraped data is for market intelligence purposes
- **Updates**: Data reflects pricing as of scrape date
- **Attribution**: All data attributed to source URLs
- **Disclaimer**: Prices may change without notice

## 🚀 Next Steps

### Immediate (Phase 1)
1. [ ] Complete NetOne, Telecel data extraction
2. [ ] Add missing provider contact info
3. [ ] Fill in service descriptions
4. [ ] Add USSD activation codes

### Short-term (Phase 2)
1. [ ] Implement Selenium for JS-heavy sites
2. [ ] Add historical price tracking
3. [ ] Create dashboard visualization
4. [ ] Build API endpoint

### Long-term (Phase 3)
1. [ ] Real-time price monitoring
2. [ ] Competitor analysis module
3. [ ] Customer sentiment analysis
4. [ ] Predictive pricing models

## 📞 Support

### Common Issues

**Q: Scraper returns empty results**
- Check website URLs are accessible
- Ensure BeautifulSoup installed correctly
- Review logs for errors

**Q: Prices appear incorrect**
- Verify exchange rate data
- Check original website for currency
- Review `confidence_score` field

**Q: Missing provider data**
- Add custom scraper for that provider
- Check if site blocks scrapers (User-Agent issue)
- Consider manual data entry + Selenium

### Help & Debugging

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python advanced_telecom_scraper.py

# Test single provider
python -c "
from advanced_telecom_scraper import EconetScraper
scraper = EconetScraper()
offerings = scraper.scrape()
print(f'Collected {len(offerings)} offerings')
"
```

## 📝 License

This scraper is for market intelligence and research purposes only. Ensure compliance with each provider's terms of service.

## 🤝 Contributing

To add new providers or features:

1. Create a new Scraper class (inherit from `ScraperBase`)
2. Implement `scrape()` method
3. Register in `MarketIntelligenceCollector`
4. Test and validate data
5. Update documentation

---

**Last Updated**: June 8, 2026
**Scraper Version**: 2.0
**Python Version**: 3.7+
