# Missing Fields Analysis Report

**Generated**: June 8, 2026  
**Analyzer**: Market Intelligence Scraper v2.0

## Executive Summary

Out of 44 defined data fields, the current dataset populates **24 fields (54.5%)** with actual values. This analysis identifies the 20 missing fields and provides a prioritized collection roadmap.

---

## Missing Fields Breakdown

### CRITICAL PRIORITY (Must Have)

#### 1. Provider Contact Information
**Fields**: `provider_email`, `provider_phone`
**Current Status**: EMPTY (0%)
**Importance**: HIGH
**Impact**: Essential for B2B queries, support escalation, partnership

**Known Values**:
```
Provider               Email                          Phone
Econet                customercare@econet.co.zw      +263 242 708000
NetOne                support@netone.co.zw           +263 242 759911
Telecel               support@telecel.co.zw          +263 242 799999
TelOne                clientservices@telone.co.zw    +263 242 700950
Tagtel                support@tagtel.co.zw           +263 242 794794
```

**Collection Method**: Website footer/contact pages, manual verification

---

#### 2. Service Descriptions
**Field**: `service_description`
**Current Status**: 50% populated
**Importance**: HIGH
**Impact**: Users need context about what each bundle includes

**Examples Needed**:
- Broadband: "Fixed-line fiber internet, 30 Mbps download, unlimited usage"
- Data Bundle: "Mobile data valid on 4G/LTE networks, includes WhatsApp"
- Voice: "On-net calls at reduced rates, voicemail included"
- SMS: "Local SMS only, does not include international"

**Collection Method**: Website bundle descriptions, promotional materials

---

#### 3. Activation Methods & USSD Codes
**Fields**: `activation_method`, `promotion_code`
**Current Status**: 30% populated
**Importance**: HIGH
**Impact**: Users need to know how to activate bundles

**Examples**:
```
Service                Provider      USSD Code        Web/App
VALUE BUNDLE 1GB       NetOne         *379#           Online
SMS Bundle             Econet         *108#           MyEconet App
Daily Data Bundle      Econet         *150#           Web
Private WiFi           Econet         N/A             Web/Retail
```

**Collection Method**: Provider USSD guides, website help sections

---

### HIGH PRIORITY (Should Have)

#### 4. Data Breakdown Details
**Fields**: `peak_data_gb`, `off_peak_data_gb`, `total_data_gb`
**Current Status**: 40% populated
**Importance**: HIGH
**Impact**: Users need to understand peak/off-peak restrictions

**Gap**: Most bundles show only total_data_gb; peak/off-peak breakdown missing for Econet/NetOne

**Collection Method**: Bundle detail pages, plan comparison tables

---

#### 5. Data Rollover Policy
**Field**: `data_rollover`
**Current Status**: EMPTY (0%)
**Importance**: HIGH
**Impact**: Affects actual value of bundle (whether unused data carries to next period)

**Questions to Answer**:
- Does unused data expire or rollover?
- Rollover period (same month, next month, never)?
- Any rollover limits?

**Collection Method**: T&Cs documents, customer support, FAQ pages

---

#### 6. Auto-Renewal Policy
**Field**: `auto_renewal`
**Current Status**: EMPTY (0%)
**Importance**: MEDIUM
**Impact**: Customers need to know if bundles auto-renew or are one-time

**Collection Method**: Bundle T&Cs, promotional terms

---

#### 7. Service Validity Period
**Field**: `validity`
**Current Status**: 80% populated (mostly "Days")
**Gap**: Some entries lack exact validity (e.g., "till midnight" vs "24 hours")

**Needed Improvements**:
- Standardize to: "X Days", "X Hours", "X Minutes", "Till HH:MM"
- Document timezone (EAT/CAT)
- Clarify expiration time (midnight local time, etc.)

---

### MEDIUM PRIORITY (Nice to Have)

#### 8. International Roaming Details
**Field**: `international_roaming`
**Current Status**: EMPTY (0%)
**Importance**: MEDIUM
**Impact**: Business travelers need roaming info

**Questions**:
- Which countries/regions supported?
- Data rates in roaming?
- Roaming included or additional cost?

**Collection Method**: Roaming pages on provider websites

---

#### 9. Included Features & Benefits
**Field**: `included_features` (JSON array)
**Current Status**: 5% populated
**Importance**: MEDIUM
**Impact**: Bundles may include extra benefits (free calls, rollover, etc.)

**Examples Needed**:
```json
{
  "service_name": "Private WiFi 55GB",
  "included_features": [
    "Unlimited On-Net calls",
    "Data rollover 50%",
    "24-hour customer support",
    "Free device registration"
  ]
}
```

**Collection Method**: Bundle detail sections, promotional material

---

#### 10. Speed Specifications (Broadband)
**Field**: `speed_mbps`
**Current Status**: EMPTY (0%) for broadband
**Importance**: HIGH for ISPs
**Impact**: ISP customers need to know download/upload speeds

**Gap**: TelOne packages documented but without speeds

**Collection Method**: ISP product pages, technical specifications

---

#### 11. Internet Data Limits
**Field**: Need new: `monthly_data_cap_gb`, `speed_after_cap`
**Current Status**: N/A
**Importance**: MEDIUM
**Impact**: "Capped" vs "Uncapped" differs by exact limits and throttling

**Collection Method**: Broadband plan pages, T&Cs

---

#### 12. Coverage Areas
**Field**: `coverage_areas`
**Current Status**: EMPTY (0%)
**Importance**: MEDIUM
**Impact**: Users need to know if service available in their area

**Collection Method**: Coverage maps, service availability checker

---

### LOWER PRIORITY (Future Enhancement)

#### 13-20. Data Enrichment Fields

| Field | Current | Importance | Use Case |
|-------|---------|-----------|----------|
| `competitor_analysis` | 0% | Low | Market positioning |
| `data_last_updated` | 5% | Medium | Data staleness tracking |
| `expiry_date` (promo) | 0% | Medium | Promo validity |
| `market_segment` | 30% | Medium | Customer targeting |
| `terms_conditions` | 10% | Medium | Legal reference |
| `device_compatibility` | 0% | Low | Tech specs |
| `reviews_rating` | 0% | Low | Customer feedback |
| `historical_price` | 0% | Low | Trend analysis |

---

## Data Completion Roadmap

### Phase 1: CRITICAL (This Sprint)
**Target**: Reach 75% field population
**Effort**: 2-3 hours manual research + code updates

**Tasks**:
- [ ] Add provider contact info (emails/phones)
- [ ] Complete service descriptions for top 20 bundles
- [ ] Document USSD codes for all data bundles
- [ ] Standardize validity format across all records

**Expected Outcome**:
```
Before: 24/44 fields (54.5%)
After:  35/44 fields (79.5%)
```

### Phase 2: HIGH PRIORITY (Next Sprint)
**Target**: Reach 85% field population
**Effort**: 4-6 hours research + Selenium automation

**Tasks**:
- [ ] Implement data rollover scraping (T&Cs documents)
- [ ] Add peak/off-peak breakdown for all bundles
- [ ] Extract speed specs for broadband
- [ ] Document international roaming per provider

**Expected Outcome**:
```
Before: 35/44 fields (79.5%)
After:  39/44 fields (88.6%)
```

### Phase 3: MEDIUM PRIORITY (Following Sprint)
**Target**: Reach 95% field population
**Effort**: 8-10 hours research + API integration

**Tasks**:
- [ ] Add included features (JSON extraction)
- [ ] Map coverage areas (API integration)
- [ ] Set up auto-renewal tracking
- [ ] Create historical price database

**Expected Outcome**:
```
Before: 39/44 fields (88.6%)
After:  42/44 fields (95.5%)
```

---

## Collection Methods by Source

### Tier 1: Official Website (Best Quality - 95%+ confidence)
- Provider contact pages
- Product specification sheets
- Pricing pages & bundle details
- FAQ sections
- Terms & Conditions documents

**Providers**: All (Econet, NetOne, Telecel, TelOne, Africom, etc.)

### Tier 2: Customer Support
- Email support queries
- Chat support transcripts
- Phone call notes
- Help desk FAQs

**Effort**: Medium (requires direct contact)
**Quality**: 85-90% confidence

### Tier 3: Third-party Sources
- News articles
- Tech blogs
- Customer review sites
- Industry reports

**Effort**: Low
**Quality**: 70-80% confidence
**Notes**: Cross-reference with official sources

### Tier 4: Inference/Estimation
- Compare similar bundles
- Industry standards
- Competitor benchmarking

**Effort**: Low
**Quality**: 60-70% confidence
**Notes**: Mark as estimated in confidence_score

---

## Sample Missing Data for Major Providers

### ECONET WIRELESS

```
Provider: Econet Wireless Zimbabwe
Missing Info:
- Contact person names
- Office addresses
- Live chat support URL
- Data rollover policy (unknown)
- International roaming rates
- Device compatibility (bundles vs 2G/3G/4G)
```

### NETONE

```
Provider: NetOne Cellular
Missing Info:
- Complete bundle descriptions
- Exact USSD codes for all plans
- Peak/off-peak breakdown
- Coverage map URL
- Enterprise service terms
- Device compatibility
```

### TELONE

```
Provider: TelOne
Missing Info:
- Exact Mbps speeds per package
- Data caps for "capped" packages
- Throttling speeds after cap
- Installation costs
- Router rental/purchase fees
- Modem specifications
```

---

## Implementation Checklist

### For Each Missing Field:

- [ ] Identify primary source (official website)
- [ ] Identify backup sources (support, news)
- [ ] Document extraction method (CSS selectors, regex, manual)
- [ ] Create extraction code/template
- [ ] Test on 2-3 records for accuracy
- [ ] Update database/CSV
- [ ] Validate in exported files

### Quality Assurance:

- [ ] No null values for high-priority fields
- [ ] Confidence scores reflect source quality
- [ ] Data timestamps current (< 7 days old)
- [ ] URLs validated (working & relevant)
- [ ] Duplicate records removed
- [ ] Formatting consistent (case, units, etc.)

---

## Field Completion Status Matrix

```
FIELD NAME                   | COMPLETION | PRIORITY | STATUS
----------------------------------------------------------
provider_name                | 100%       | Critical | ✅ Complete
provider_type                | 100%       | Critical | ✅ Complete
provider_website             | 100%       | Critical | ✅ Complete
service_category             | 100%       | Critical | ✅ Complete
service_name                 | 100%       | Critical | ✅ Complete
unit_type                    | 100%       | Critical | ✅ Complete
price_usd                    | 95%        | Critical | ✅ Nearly complete
billing_period               | 90%        | Critical | ✅ Nearly complete
validity                     | 80%        | Critical | ⚠️  Partial
----------------------------------------------------------
service_description          | 50%        | High     | 🔴 Incomplete
provider_email               | 0%         | High     | 🔴 Missing
provider_phone               | 0%         | High     | 🔴 Missing
activation_method            | 30%        | High     | 🔴 Incomplete
promotion_code               | 20%        | High     | 🔴 Mostly missing
total_data_gb                | 40%        | High     | 🔴 Incomplete
data_rollover                | 0%         | High     | 🔴 Missing
----------------------------------------------------------
peak_data_gb                 | 40%        | Medium   | 🔴 Incomplete
off_peak_data_gb             | 40%        | Medium   | 🔴 Incomplete
speed_mbps                   | 0%         | Medium   | 🔴 Missing
international_roaming        | 0%         | Medium   | 🔴 Missing
included_features            | 5%         | Medium   | 🔴 Mostly missing
auto_renewal                 | 0%         | Medium   | 🔴 Missing
coverage_areas               | 0%         | Medium   | 🔴 Missing
----------------------------------------------------------
market_segment               | 30%        | Medium   | ⚠️  Partial
confidence_score             | 90%        | Low      | ✅ Good
source_url                   | 95%        | Low      | ✅ Good
scraped_date                 | 100%       | Low      | ✅ Complete
```

---

## Next Steps

1. **This Week**: Collect provider contact information (2 hours)
2. **This Sprint**: Complete service descriptions and USSD codes (4 hours)
3. **Next Sprint**: Automate T&C scraping for rollover policies (6 hours)
4. **Ongoing**: Monitor price changes and update weekly

---

**Report Generated**: 2026-06-08 14:16:23 UTC  
**Data Freshness**: Current as of report date  
**Total Records**: 34  
**Avg Field Population**: 54.5%
