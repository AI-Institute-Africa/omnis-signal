# Zimbabwe Telecom Scraper - Quick Reference

## 🚀 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run scraper
python advanced_telecom_scraper.py

# 3. View data
# - Open: zimbabwe_telecom_intelligence.xlsx (Excel)
# - Or: zimbabwe_telecom_intelligence.csv (any text editor/Excel)
# - Or: cat zimbabwe_telecom_intelligence.json (command line)
```

---

## 📊 Data Provided

### Current Coverage: 34 Records

| Provider | Records | Categories | Fields Populated |
|----------|---------|------------|-----------------|
| Econet | 22 | Broadband, Data, SMS, Social | 54.5% |
| TelOne | 10 | Broadband | 54.5% |
| NetOne | 1 | Data Bundle | 54.5% |
| Tagtel | 1 | Data Bundle | 54.5% |
| **TOTAL** | **34** | **4+** | **54.5%** |

### Service Categories

- 🌐 **Broadband Plans** (15 records)
  - Private WiFi bundles
  - Monthly/weekly/daily data bundles
  - ISP packages
  
- 📱 **Data Bundles** (5 records)
  - Standalone mobile data
  - MVNO offerings
  
- 💬 **SMS Bundles** (6 records)
  - Daily/weekly SMS packages
  - SMS counts and pricing
  
- 👥 **Social Media Bundles** (8 records)
  - WhatsApp, Facebook, Instagram, X
  - MB allocations per service

---

## 🔑 Key Fields (Always Populated)

```
✅ provider_name        → "Econet Wireless Zimbabwe"
✅ service_name         → "Private WiFi Bundle 55GB"
✅ unit_type            → "GB" or "MB" or "SMS Count"
✅ unit_value           → 55 (numeric)
✅ price_usd            → 2341.00 (normalized USD)
✅ billing_period       → "Monthly", "Daily", "Weekly"
✅ validity             → "30 Days", "24 Hours", etc.
✅ service_category     → "broadband_plan", "data_bundle", etc.
✅ confidence_score     → 60-100 (data reliability)
✅ source_url           → Where data was scraped from
```

---

## ❓ Missing Fields (0% Populated)

Priority order to fill:

### 🔴 CRITICAL (Do First)
1. **provider_email** - Contact email
2. **provider_phone** - Phone number
3. **activation_method** - "USSD: *379#", "Web", "App"
4. **promotion_code** - USSD codes or coupon codes
5. **service_description** - What the bundle includes

### 🟠 HIGH (Do Next)
6. **data_rollover** - true/false (does unused data carry over?)
7. **international_roaming** - Roaming countries/rates
8. **speed_mbps** - For broadband plans
9. **coverage_areas** - Geographic coverage
10. **included_features** - Free add-ons

---

## 📋 File Structure

```
scraper-hub-v1 (2)/
├── README.md                              ← Start here!
├── SCHEMA.md                              ← Data field definitions
├── MISSING_FIELDS_ANALYSIS.md             ← What's missing & priority
├── QUICK_REFERENCE.md                     ← This file
│
├── advanced_telecom_scraper.py            ← Main scraper (DO USE THIS)
├── telecom_scraper.py                     ← Basic template
├── setup.py                               ← Auto-setup script
├── requirements.txt                       ← Python dependencies
│
├── zimbabwe_telecom_intelligence.csv      ← Exported data (CSV)
├── zimbabwe_telecom_intelligence.json     ← Exported data (JSON)
└── zimbabwe_telecom_intelligence.xlsx     ← Exported data (Excel)
```

---

## 🎯 Common Tasks

### Task 1: Filter bundles under $5 USD

```python
import pandas as pd
df = pd.read_csv('zimbabwe_telecom_intelligence.csv')
cheap_bundles = df[df['price_usd'] < 5.0]
print(cheap_bundles[['service_name', 'price_usd', 'unit_value']])
```

**Output**:
```
service_name                  price_usd  unit_value
SMS Daily 13 SMSs            1.05       13
WhatsApp (15MB)              2.40       15
Data Monthly Bundle (100MB)  14.00      100
```

---

### Task 2: Find all Econet data bundles

```python
econet_data = df[
    (df['provider_name'] == 'Econet Wireless Zimbabwe') & 
    (df['service_category'] == 'data_bundle')
]
print(econet_data[['service_name', 'unit_value', 'price_usd', 'validity']])
```

---

### Task 3: Compare SMS pricing across providers

```python
sms_bundles = df[df['service_category'] == 'sms_bundle']
grouped = sms_bundles.groupby('provider_name')['price_usd'].agg(['min', 'max', 'mean'])
print(grouped)
```

---

### Task 4: Export data as structured JSON API

```python
import json
data = df.to_dict('records')
with open('api.json', 'w') as f:
    json.dump(data, f, indent=2)
# Now query with: curl http://api.local/api.json | jq '.[] | select(.provider_name=="Econet")'
```

---

## 🔄 How to Add Missing Data

### For Provider Contact Info:
1. Visit provider website
2. Look for: Contact Us, About Us, Support
3. Copy email and phone
4. Update spreadsheet or code

**Example**:
```python
# In advanced_telecom_scraper.py, EconetScraper.__init__()
self.provider_email = 'customercare@econet.co.zw'
self.provider_phone = '+263 242 708000'
```

### For USSD Codes:
1. Visit provider's "How to Buy" or "Bundles" page
2. Look for activation instructions
3. Copy USSD format (e.g., "*379#")
4. Add to `promotion_code` field

**Example**:
```python
self.add_offering(
    service_name='VALUE BUNDLE',
    promotion_code='*379#',
    activation_method='USSD: *379# or dial *111#'
)
```

### For Service Descriptions:
1. Visit provider bundle detail page
2. Read benefits/features section
3. Write 1-2 sentence summary
4. Update `service_description` field

**Example**:
```python
service_description='Private WiFi broadband bundle with 55GB data valid for 30 days. Includes unlimited on-net calls.'
```

---

## 📈 Data Quality Checklist

Before using data in production, verify:

- [ ] **No empty prices**: All bundles have `price_usd` > 0
- [ ] **No duplicate records**: Each bundle unique by (provider, name, price)
- [ ] **Valid URLs**: All `source_url` start with http/https
- [ ] **Consistency**: Similar bundles have consistent format
- [ ] **Freshness**: `scraped_date` is recent (< 7 days old)
- [ ] **Confidence scores**: Reflect data source quality

---

## 🛠️ Troubleshooting

### Problem: Empty CSV file
**Solution**: Check if scraper ran successfully. Look for errors in output.

### Problem: Prices look wrong
**Solution**: Verify `currency` field matches `price_local`. Check exchange rate.

### Problem: Missing provider data
**Solution**: Create new Scraper class (see README.md → Extension Guide)

### Problem: Website changed, scraper broken
**Solution**: 
1. Update website URL in `PROVIDERS` dict
2. Verify HTML structure hasn't changed
3. Use Selenium for JavaScript-heavy sites

---

## 📞 Provider Contact Quick Reference

| Provider | Website | Support Email | Phone |
|----------|---------|---------------|-------|
| Econet | econet.co.zw | customercare@econet.co.zw | +263 242 708000 |
| NetOne | netone.co.zw | support@netone.co.zw | +263 242 759911 |
| Telecel | telecel.co.zw | support@telecel.co.zw | +263 242 799999 |
| TelOne | telone.co.zw | clientservices@telone.co.zw | +263 242 700950 |
| Tagtel | tagtel.co.zw | support@tagtel.co.zw | +263 242 794794 |
| Africom | africom.co.zw | info@africom.co.zw | +263 242 xxx |
| Liquid Home | liquidhome.co.zw | support@liquidhome.co.zw | +263 xxx |

---

## 🔄 Regular Maintenance

### Weekly
- [ ] Run scraper: `python advanced_telecom_scraper.py`
- [ ] Check for price changes in CSV
- [ ] Note any new bundles

### Monthly
- [ ] Update missing fields (contact info, descriptions)
- [ ] Add new providers if found
- [ ] Review confidence scores

### Quarterly
- [ ] Analyze pricing trends
- [ ] Identify discontinued bundles
- [ ] Update documentation

---

## 💡 Pro Tips

1. **Use Excel filtering**: Open .xlsx in Excel, use Data → AutoFilter
2. **Monitor prices with Python**: Write script to compare month-to-month
3. **Create dashboard**: Import JSON into BI tool (Tableau, Power BI, etc.)
4. **Schedule updates**: Use cron (Linux) or Task Scheduler (Windows)
5. **Version control**: Commit CSV/JSON to Git for history tracking

---

## 📚 Documentation Map

```
Start here:
  README.md ← Overview
      ↓
  SCHEMA.md ← Understand fields
      ↓
  MISSING_FIELDS_ANALYSIS.md ← See what's missing
      ↓
  QUICK_REFERENCE.md ← This file (how to use data)
      ↓
  advanced_telecom_scraper.py ← Understand code
```

---

## ⚡ One-Liners

```bash
# Count records by provider
cut -d',' -f1 zimbabwe_telecom_intelligence.csv | sort | uniq -c

# Show only data bundles
grep 'data_bundle' zimbabwe_telecom_intelligence.csv | cut -d',' -f5,17

# Find cheapest bundle
sort -t',' -k17 -n zimbabwe_telecom_intelligence.csv | head -5

# Export just Econet data
grep 'Econet' zimbabwe_telecom_intelligence.csv > econet_bundles.csv
```

---

**Last Updated**: June 8, 2026  
**Current Data Records**: 34  
**Field Completion**: 54.5%  
**Next Update Target**: 75% completion
