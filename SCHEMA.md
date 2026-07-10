# Zimbabwe Telecom Market Intelligence Schema

## Overview
This document defines the complete data schema for collecting telecom market intelligence from Zimbabwe operators and ISPs.

## Field Definitions

### Provider Information
- **provider_name**: Official company name (e.g., "Econet Wireless Zimbabwe")
- **provider_type**: Classification (MNO, ISP, MVNO, Telecom, Fixed Line)
- **provider_website**: Official company website URL
- **contact_email**: Support/general contact email
- **contact_phone**: Primary contact number
- **coverage_areas**: Service coverage (National, Regional, Urban/Rural)

### Service Information
- **service_category**: Type of service
  - `voice_bundle` - Voice/minutes packages
  - `data_bundle` - Mobile data packages
  - `sms_bundle` - SMS/text packages
  - `broadband_plan` - Fixed broadband/ISP plans
  - `social_bundle` - Social media-specific (WhatsApp, Facebook, Instagram)
  - `device` - Phone/equipment sales
  - `enterprise_service` - B2B offerings
  - `sim_card` - SIM card sales
  - `general_service` - Other services (info, news, etc.)

- **service_name**: Specific product name (e.g., "Private WiFi Bundle 55GB")
- **service_description**: Detailed service description
- **launch_date**: When service became available (if known)
- **status**: active, discontinued, promotional, seasonal

### Unit & Volume Information
- **unit_type**: Unit of measurement
  - For data: MB, GB
  - For voice: Minutes, Hours
  - For SMS: SMS Count, SMS per day
  - For broadband: Mbps, GB/month
  - For others: as applicable

- **unit_value**: Numeric value of unit (e.g., 55 for 55GB)
- **peak_data_gb**: Peak hours data (GB) if applicable
- **off_peak_data_gb**: Off-peak hours data (GB) if applicable
- **total_data_gb**: Total combined data
- **speed_mbps**: Internet speed in Mbps (for broadband)

### Pricing Information
- **price_usd**: Price in USD (normalized currency)
- **price_local**: Price in local currency (ZWG, ZWD, etc.)
- **price_string**: Original price as shown on website (for validation)
- **currency**: Currency code (USD, ZWG, ZWD)
- **billing_period**: How service is billed
  - Daily, Weekly, Monthly, Annual, Hourly, One-time, Variable

- **promo_price**: Discounted price (if promotional)
- **regular_price**: Non-promotional price

### Validity & Terms
- **validity**: How long the service is valid
  - e.g., "30 Days", "7 Days", "24 Hours", "1 Hour", "Till midnight", "Valid forever"

- **auto_renewal**: Whether service auto-renews (true/false)
- **expiry_date**: When specific promotional pricing ends (if applicable)
- **terms_conditions**: URL to T&Cs or summary

### Features & Benefits
- **included_features**: JSON array of included features
  - Example: ["Free calls to Econet", "2x data bonus", "WhatsApp included"]

- **data_rollover**: Whether unused data carries over
- **international_roaming**: Roaming benefits
- **unlimited_offering**: Whether it's unlimited (true/false)
- **additional_features**: Free add-ons, bonuses, or special features

### Data Quality & Provenance
- **confidence_score**: 60-100 (reliability of data)
  - 100: Directly from official pricing page
  - 80+: From company website but not directly verified
  - 60-79: From third-party sources or inferred
  - <60: Estimated or outdated

- **source_url**: URL where data was scraped
- **source_type**: official_website, news_article, competitor_site, social_media, customer_review
- **scraped_date**: ISO 8601 timestamp of when data was collected
- **data_last_updated**: When data was last updated on source

### Market Intelligence
- **competitor_analysis**: Notes on competitive positioning
- **market_segment**: Target customer (Consumer, SME, Enterprise, Student, etc.)
- **promotion_code**: Activation code or USSD code (e.g., "*379#", "BUNDLE123")
- **activation_method**: How to activate (USSD, Web, App, In-store, SMS)
- **notes**: Additional notes or observations

---

## Example Record (Econet Private WiFi Bundle 55GB)

```json
{
  "provider_name": "Econet Wireless Zimbabwe",
  "provider_type": "MNO",
  "provider_website": "https://www.econet.co.zw",
  "service_category": "broadband_plan",
  "service_name": "Private WiFi Bundle 55GB",
  "unit_type": "GB",
  "unit_value": 55,
  "price_usd": 2341.00,
  "price_local": "2341.00 ZWG",
  "currency": "ZWG",
  "billing_period": "Monthly",
  "validity": "30 Days",
  "peak_data_gb": 55,
  "off_peak_data_gb": null,
  "confidence_score": 80,
  "source_url": "https://www.econet.co.zw/bundles/",
  "scraped_date": "2026-06-08T13:57:00Z",
  "activation_method": "Web/App"
}
```

---

## Missing Fields in Current Dataset

Based on the provided data, these fields are currently missing or incomplete:

1. **Provider contact information** - No emails, phone numbers, or support channels
2. **Service descriptions** - Many entries lack context/description
3. **Promotion codes** - No USSD codes or activation methods
4. **International roaming** - Roaming benefits not documented
5. **Data rollover** - Whether data carries over
6. **Auto-renewal status** - Unknown for most bundles
7. **Competitive analysis** - No market positioning data
8. **Target segments** - Who these services are marketed to
9. **Expiry dates for promos** - Promotional validity periods
10. **Speed specifications** - Mbps for broadband plans
11. **Enterprise service details** - B2B pricing and SLA terms
12. **Coverage areas** - Geographic coverage for each service
13. **Device specifications** - For phone/equipment sales
14. **API/integration details** - Technical integration information
15. **Historical pricing** - Price trends over time

---

## Data Collection Priority

### High Priority (Complete ASAP)
- Service names and descriptions
- Pricing (USD normalization)
- Validity periods
- Activation methods (USSD codes)
- Provider contact info

### Medium Priority (Complete within sprint)
- Included features/benefits
- Data rollover policies
- International roaming
- Auto-renewal status
- Confidence scores

### Low Priority (Future enhancement)
- Historical pricing trends
- Competitive analysis
- Customer reviews/ratings
- API documentation
- Integration methods

---

## Data Quality Checklist

- [ ] All prices normalized to USD and local currency
- [ ] All validity periods documented (Days/Hours/Minutes)
- [ ] Provider contact information complete
- [ ] Service descriptions non-empty
- [ ] Confidence scores assigned based on source
- [ ] URLs verified and accessible
- [ ] Date formats ISO 8601 compliant
- [ ] Special characters properly encoded
- [ ] No duplicate records
- [ ] Missing fields marked as null (not blank strings)
