"""
Banking Sector Database Seed
Implements:
1. All 23 Zimbabwean Bank Providers
2. PART A: 4 Flat Consumer Banking Categories (savings-accounts, current-accounts, nostro-fca-accounts, banks) + Attribute Schemas
3. PART B: The 3-Level Banking Fee Hierarchy (fee_category -> subcategory -> revenue_line) + Revenue Line Attribute Schemas
4. Bank Directory Listings under 'banks' with USSD codes and channel flags
"""
import uuid
from typing import Dict, Any, List
from app.db.session import SessionLocal
from app.db.models.catalog import (
    SectorConfig, Category, AttributeSchemaField, Provider,
    Listing, ListingPriceHistory,
    SectorStatus, CategoryLevel, AttributeDataType, QualityAxis,
    ListingStatus, FreshnessStatus, ListingUpdateSource
)


def _uid() -> str:
    return str(uuid.uuid4())


# ============================================================================
# 1. 23 ZIMBABWEAN BANKS DIRECTORY
# ============================================================================
BANK_PROVIDERS = [
    {
        "name": "CBZ Bank",
        "bank_type": "commercial",
        "website_url": "https://www.cbz.co.zw",
        "corporate_domain": "cbz.co.zw",
        "ussd_code": "*234#",
        "ussd_brand": "CBZ Touch",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "Stanbic Bank",
        "bank_type": "commercial",
        "website_url": "https://www.stanbicbank.co.zw",
        "corporate_domain": "stanbic.co.zw",
        "ussd_code": "*247#",
        "ussd_brand": "Stanbic Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "Standard Chartered",
        "bank_type": "commercial",
        "website_url": "https://www.sc.com/zw",
        "corporate_domain": "sc.com",
        "ussd_code": "*200#",
        "ussd_brand": "SC Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": False,
            "channel_call_centre": True
        }
    },
    {
        "name": "BancABC",
        "bank_type": "commercial",
        "website_url": "https://www.bancabc.co.zw",
        "corporate_domain": "bancabc.co.zw",
        "ussd_code": "*222#",
        "ussd_brand": "A360",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "FBC Bank",
        "bank_type": "commercial",
        "website_url": "https://www.fbc.co.zw",
        "corporate_domain": "fbc.co.zw",
        "ussd_code": "*220#",
        "ussd_brand": "FBC Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "NMB Bank",
        "bank_type": "commercial",
        "website_url": "https://www.nmbz.co.zw",
        "corporate_domain": "nmbz.co.zw",
        "ussd_code": "*241#",
        "ussd_brand": "NMBConnect",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "Steward Bank",
        "bank_type": "commercial",
        "website_url": "https://www.stewardbank.co.zw",
        "corporate_domain": "stewardbank.co.zw",
        "ussd_code": "*210#",
        "ussd_brand": "Square",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "ZB Bank",
        "bank_type": "commercial",
        "website_url": "https://www.zb.co.zw",
        "corporate_domain": "zb.co.zw",
        "ussd_code": "*400#",
        "ussd_brand": "E-Wallet",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "Ecobank",
        "bank_type": "commercial",
        "website_url": "https://www.ecobank.com/zw",
        "corporate_domain": "ecobank.com",
        "ussd_code": "*326#",
        "ussd_brand": "Ecobank Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "First Capital Bank",
        "bank_type": "commercial",
        "website_url": "https://www.firstcapitalbank.co.zw",
        "corporate_domain": "firstcapitalbank.co.zw",
        "ussd_code": "*227#",
        "ussd_brand": "FCB Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": False, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "Nedbank",
        "bank_type": "commercial",
        "website_url": "https://www.nedbank.co.zw",
        "corporate_domain": "nedbank.co.zw",
        "ussd_code": "*119#",
        "ussd_brand": "Nedbank Money",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "Metbank",
        "bank_type": "commercial",
        "website_url": "https://www.metbank.co.zw",
        "corporate_domain": "metbank.co.zw",
        "ussd_code": "*235#",
        "ussd_brand": "MetMobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": False,
            "channel_call_centre": True
        }
    },
    {
        "name": "AFC Commercial Bank",
        "bank_type": "commercial",
        "website_url": "https://www.afcholdings.co.zw",
        "corporate_domain": "afcholdings.co.zw",
        "ussd_code": "*246#",
        "ussd_brand": "AFC Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "CABS",
        "bank_type": "building society",
        "website_url": "https://www.cabs.co.zw",
        "corporate_domain": "cabs.co.zw",
        "ussd_code": "*227#",
        "ussd_brand": "CABS Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "FBC Building Society",
        "bank_type": "building society",
        "website_url": "https://www.fbc.co.zw",
        "corporate_domain": "buildingsociety.fbc.co.zw",
        "ussd_code": "*220#",
        "ussd_brand": "FBC Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "National Building Society",
        "bank_type": "building society",
        "website_url": "https://www.nbs.co.zw",
        "corporate_domain": "nbs.co.zw",
        "ussd_code": "*114#",
        "ussd_brand": "NBS Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "POSB",
        "bank_type": "commercial",
        "website_url": "https://www.posb.co.zw",
        "corporate_domain": "posb.co.zw",
        "ussd_code": "*223#",
        "ussd_brand": "POSB Mobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": True,
            "channel_agency": True, "channel_branch": True, "channel_atm": True,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "EmpowerBank",
        "bank_type": "microfinance",
        "website_url": "https://www.empowerbank.co.zw",
        "corporate_domain": "empowerbank.co.zw",
        "ussd_code": "*215#",
        "ussd_brand": "EmpowerMobile",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": False,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "GetBucks",
        "bank_type": "microfinance",
        "website_url": "https://www.getbucks.co.zw",
        "corporate_domain": "getbucks.co.zw",
        "ussd_code": "*444#",
        "ussd_brand": "GetBucks App",
        "channels": {
            "channel_mobile_app": True, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": False,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "InnBucks",
        "bank_type": "microfinance",
        "website_url": "https://www.innbucks.co.zw",
        "corporate_domain": "innbucks.co.zw",
        "ussd_code": "*569#",
        "ussd_brand": "InnBucks App",
        "channels": {
            "channel_mobile_app": True, "channel_internet": False, "channel_whatsapp": False,
            "channel_agency": True, "channel_branch": True, "channel_atm": False,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": True,
            "channel_call_centre": True
        }
    },
    {
        "name": "Zimbabwe Women Microfinance Bank",
        "bank_type": "microfinance",
        "website_url": "https://www.zwmb.co.zw",
        "corporate_domain": "zwmb.co.zw",
        "ussd_code": "*229#",
        "ussd_brand": "ZWMB Mobile",
        "channels": {
            "channel_mobile_app": False, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": True, "channel_branch": True, "channel_atm": False,
            "channel_pos": True, "channel_zipit": True, "channel_wallet_link": False,
            "channel_call_centre": True
        }
    },
    {
        "name": "IDBZ",
        "bank_type": "development",
        "website_url": "https://www.idbz.co.zw",
        "corporate_domain": "idbz.co.zw",
        "ussd_code": None,
        "ussd_brand": None,
        "channels": {
            "channel_mobile_app": False, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": False,
            "channel_pos": False, "channel_zipit": False, "channel_wallet_link": False,
            "channel_call_centre": True
        }
    },
    {
        "name": "AFC Land Bank",
        "bank_type": "development",
        "website_url": "https://www.afcholdings.co.zw",
        "corporate_domain": "landbank.afcholdings.co.zw",
        "ussd_code": "*246#",
        "ussd_brand": "AFC Land",
        "channels": {
            "channel_mobile_app": False, "channel_internet": True, "channel_whatsapp": False,
            "channel_agency": False, "channel_branch": True, "channel_atm": False,
            "channel_pos": False, "channel_zipit": False, "channel_wallet_link": False,
            "channel_call_centre": True
        }
    }
]


# ============================================================================
# 2. PART A: FLAT CONSUMER BANKING CATEGORIES
# ============================================================================
FLAT_BANKING_CATEGORIES = [
    {
        "slug": "savings-accounts",
        "name": "Savings accounts",
        "synonyms": ["savings account", "deposit account"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "monthly_fee", "label": "Monthly fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 0, "quality_axis": QualityAxis.VALUE},
            {"key": "min_balance", "label": "Min. balance", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
            {"key": "interest_rate", "label": "Interest rate", "data_type": AttributeDataType.NUMBER, "unit": "% p.a.", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
            {"key": "atm_withdrawal_fee", "label": "ATM withdrawal fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3, "quality_axis": QualityAxis.VALUE},
            {"key": "mobile_app", "label": "Mobile app", "data_type": AttributeDataType.STRING, "unit": None, "sort_order": 4, "is_comparable": True},
        ]
    },
    {
        "slug": "current-accounts",
        "name": "Current accounts",
        "synonyms": ["current account", "cheque account", "transactional account"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "monthly_fee", "label": "Monthly fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 0, "quality_axis": QualityAxis.VALUE},
            {"key": "min_balance", "label": "Min. balance", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
            {"key": "transaction_fee", "label": "Transaction fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
            {"key": "overdraft", "label": "Overdraft available", "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 3, "is_comparable": True},
            {"key": "branch_count", "label": "Branches", "data_type": AttributeDataType.NUMBER, "unit": None, "sort_order": 4, "is_comparable": True},
        ]
    },
    {
        "slug": "nostro-fca-accounts",
        "name": "Nostro FCA (USD) accounts",
        "synonyms": ["usd account", "foreign currency account", "dollar account", "fca account"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "monthly_fee", "label": "Monthly fee", "consumer_label": None, "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 0, "quality_axis": QualityAxis.VALUE},
            {"key": "min_balance", "label": "Min. balance", "consumer_label": "Minimum balance to open", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
            {"key": "rtgs_fee_app", "label": "RTGS Fee (App)", "consumer_label": "Sending money via app", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
            {"key": "rtgs_fee_manual", "label": "RTGS Fee (Manual/Branch)", "consumer_label": "Sending money at a branch", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3, "quality_axis": QualityAxis.VALUE},
            {"key": "channel_ussd", "label": "USSD Channel", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 4, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_agency", "label": "Agency Banking", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 5, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "customer_type", "label": "Customer type", "consumer_label": None, "data_type": AttributeDataType.ENUM, "unit": None, "sort_order": 6, "is_comparable": False},
        ]
    },
    {
        "slug": "banks",
        "name": "Banks & channels",
        "synonyms": ["bank", "which bank", "bank channels", "ussd banking", "whatsapp banking", "agency banking"],
        "level": CategoryLevel.STANDARD,
        "fields": [
            {"key": "bank_type", "label": "Bank type", "consumer_label": None, "data_type": AttributeDataType.ENUM, "unit": None, "sort_order": 0, "is_comparable": False},
            {"key": "ussd_code", "label": "USSD code", "consumer_label": "Dial-up code", "data_type": AttributeDataType.STRING, "unit": None, "sort_order": 1, "is_comparable": True},
            {"key": "ussd_brand", "label": "USSD / app brand", "consumer_label": None, "data_type": AttributeDataType.STRING, "unit": None, "sort_order": 2, "is_comparable": False},
            {"key": "channel_mobile_app", "label": "Mobile app", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 3, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_internet", "label": "Internet banking", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 4, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_whatsapp", "label": "WhatsApp banking", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 5, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_agency", "label": "Agency banking", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 6, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_branch", "label": "Branch banking", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 7, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_atm", "label": "ATM network", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 8, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_pos", "label": "POS services", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 9, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_zipit", "label": "ZIPIT enabled", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 10, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_wallet_link", "label": "Mobile-money link", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 11, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_call_centre", "label": "Call centre", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 12, "quality_axis": QualityAxis.AVAILABILITY},
            {"key": "channel_count", "label": "Channels offered", "consumer_label": "How many ways you can bank", "data_type": AttributeDataType.NUMBER, "unit": None, "sort_order": 13, "is_comparable": True},
        ]
    }
]


# ============================================================================
# 3. PART B: 3-LEVEL BANKING FEE HIERARCHY
# ============================================================================
BANKING_FEE_HIERARCHY = [
    # B1. Funded Income
    {
        "slug": "funded-income",
        "name": "Funded Income",
        "synonyms": ["interest income", "lending income", "funded"],
        "subcategories": [
            {
                "slug": "interest-income",
                "name": "Interest Income",
                "synonyms": ["interest earned", "lending revenue"],
                "revenue_lines": [
                    {
                        "slug": "consumer-loan-interest",
                        "name": "Consumer Loan Interest",
                        "channel": "mobile_banking",
                        "fields": [
                            {"key": "interest_rate", "label": "Interest Rate", "consumer_label": "Annual interest rate", "data_type": AttributeDataType.NUMBER, "unit": "% p.a.", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "max_amount", "label": "Max Loan Amount", "consumer_label": "Maximum you can borrow", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2},
                            {"key": "min_amount", "label": "Min Loan Amount", "consumer_label": "Minimum loan", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3},
                            {"key": "repayment_term_months", "label": "Repayment Term", "consumer_label": "How long to repay", "data_type": AttributeDataType.NUMBER, "unit": "months", "sort_order": 4},
                            {"key": "processing_fee", "label": "Processing Fee", "consumer_label": "Upfront fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 5, "quality_axis": QualityAxis.VALUE},
                            {"key": "collateral_required", "label": "Collateral Required", "consumer_label": "Do you need security?", "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 6},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 7, "quality_axis": QualityAxis.AVAILABILITY},
                            {"key": "available_via_internet", "label": "Available via Internet", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 8, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    },
                    {
                        "slug": "sme-loan-interest",
                        "name": "SME Loan Interest",
                        "channel": "internet_banking",
                        "fields": [
                            {"key": "interest_rate", "label": "Interest Rate", "consumer_label": "Annual interest rate", "data_type": AttributeDataType.NUMBER, "unit": "% p.a.", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "max_amount", "label": "Max Loan Amount", "consumer_label": "Maximum loan limit", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2},
                            {"key": "min_amount", "label": "Min Loan Amount", "consumer_label": "Minimum loan", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3},
                            {"key": "repayment_term_months", "label": "Repayment Term", "consumer_label": "Repayment period in months", "data_type": AttributeDataType.NUMBER, "unit": "months", "sort_order": 4},
                            {"key": "processing_fee", "label": "Processing Fee", "consumer_label": "Upfront processing fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 5, "quality_axis": QualityAxis.VALUE},
                            {"key": "collateral_required", "label": "Collateral Required", "consumer_label": "Security required", "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 6},
                            {"key": "available_via_internet", "label": "Available via Internet", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 7, "quality_axis": QualityAxis.AVAILABILITY},
                            {"key": "available_via_branch", "label": "Available via Branch", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 8, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    },
                    {
                        "slug": "mortgage-interest",
                        "name": "Mortgage / Housing Loan Interest",
                        "channel": "branch",
                        "fields": [
                            {"key": "interest_rate", "label": "Interest Rate", "consumer_label": "Mortgage interest rate", "data_type": AttributeDataType.NUMBER, "unit": "% p.a.", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "max_amount", "label": "Max Loan Amount", "consumer_label": "Maximum mortgage limit", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2},
                            {"key": "repayment_term_years", "label": "Repayment Term (years)", "consumer_label": "Mortgage tenure in years", "data_type": AttributeDataType.NUMBER, "unit": "years", "sort_order": 3},
                            {"key": "deposit_required", "label": "Deposit Required", "consumer_label": "Minimum deposit %", "data_type": AttributeDataType.NUMBER, "unit": "%", "sort_order": 4},
                            {"key": "processing_fee", "label": "Processing Fee", "consumer_label": "Valuation and legal fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 5, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_branch", "label": "Available via Branch", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 6, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    },
                    {
                        "slug": "overdraft-interest",
                        "name": "Overdraft Interest",
                        "channel": "mobile_banking",
                        "fields": [
                            {"key": "interest_rate", "label": "Interest Rate", "consumer_label": "Overdraft APR", "data_type": AttributeDataType.NUMBER, "unit": "% p.a.", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "overdraft_limit", "label": "Overdraft Limit", "consumer_label": "Maximum overdraft limit", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2},
                            {"key": "setup_fee", "label": "Setup Fee", "consumer_label": "Facility arrangement fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 4, "quality_axis": QualityAxis.AVAILABILITY},
                            {"key": "available_via_internet", "label": "Available via Internet", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 5, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    }
                ]
            },
            {
                "slug": "interest-expense",
                "name": "Interest Expense",
                "synonyms": ["interest paid", "cost of funds"],
                "revenue_lines": [
                    {
                        "slug": "savings-interest-paid",
                        "name": "Savings Interest Paid",
                        "channel": "mobile_banking",
                        "fields": [
                            {"key": "interest_rate", "label": "Interest Rate", "consumer_label": "Annual return on savings", "data_type": AttributeDataType.NUMBER, "unit": "% p.a.", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "min_deposit", "label": "Min Deposit", "consumer_label": "Minimum to open", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 3, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    }
                ]
            }
        ]
    },

    # B2. Non-Funded Income
    {
        "slug": "non-funded-income",
        "name": "Non-Funded Income",
        "synonyms": ["fees and commissions", "service charges", "non-interest income"],
        "subcategories": [
            {
                "slug": "fees-commissions",
                "name": "Fees & Commissions",
                "synonyms": ["bank charges", "service fees"],
                "revenue_lines": [
                    {
                        "slug": "monthly-account-fee",
                        "name": "Monthly Account Fee",
                        "channel": "mobile_banking",
                        "fields": [
                            {"key": "monthly_fee", "label": "Monthly fee", "consumer_label": "What you pay per month", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "min_balance", "label": "Min balance", "consumer_label": "Minimum balance to avoid fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 3, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    },
                    {
                        "slug": "transaction-fees",
                        "name": "Transaction Fees",
                        "channel": "mobile_banking",
                        "fields": [
                            {"key": "internal_transfer", "label": "Internal transfer", "consumer_label": "Same-bank transfer fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "interbank_transfer", "label": "Interbank transfer", "consumer_label": "Transfer to another bank", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "atm_withdrawal", "label": "ATM withdrawal", "consumer_label": "ATM cash withdrawal fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3, "quality_axis": QualityAxis.VALUE},
                            {"key": "pos_transaction", "label": "POS transaction", "consumer_label": "Card payment fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 4, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 5, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    },
                    {
                        "slug": "atm-fees",
                        "name": "ATM Fees",
                        "channel": "branch",
                        "fields": [
                            {"key": "own_atm", "label": "Own ATM fee", "consumer_label": "Fee at own bank's ATM", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "other_atm", "label": "Other ATM fee", "consumer_label": "Fee at another bank's ATM", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "atm_count", "label": "ATM Count", "consumer_label": "Number of ATMs nationwide", "data_type": AttributeDataType.NUMBER, "unit": "ATMs", "sort_order": 3},
                            {"key": "available_via_branch", "label": "Available via Branch", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 4, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    }
                ]
            },
            {
                "slug": "service-charges",
                "name": "Service Charges",
                "synonyms": ["penalty fees", "incidentals"],
                "revenue_lines": [
                    {
                        "slug": "minimum-balance-fee",
                        "name": "Minimum Balance Fee",
                        "channel": "mobile_banking",
                        "fields": [
                            {"key": "fee_amount", "label": "Fee Amount", "consumer_label": "Monthly penalty fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "min_balance", "label": "Min Balance Required", "consumer_label": "Balance required to avoid fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 3, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    },
                    {
                        "slug": "statement-fees",
                        "name": "Statement & Documentation Fees",
                        "channel": "internet_banking",
                        "fields": [
                            {"key": "paper_statement", "label": "Paper Statement Fee", "consumer_label": "Fee for paper statement", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "electronic_statement", "label": "Electronic Statement Fee", "consumer_label": "Fee for e-statement", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_internet", "label": "Available via Internet", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 3, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    }
                ]
            }
        ]
    },

    # B3. Trading Income
    {
        "slug": "trading-income",
        "name": "Trading Income",
        "synonyms": ["forex income", "securities income", "trading revenue"],
        "subcategories": [
            {
                "slug": "forex-income",
                "name": "Forex Income",
                "synonyms": ["foreign exchange", "currency exchange", "forex fees"],
                "revenue_lines": [
                    {
                        "slug": "forex-spread",
                        "name": "Forex Spread",
                        "channel": "branch",
                        "fields": [
                            {"key": "usd_zig_spread", "label": "USD/ZiG Spread", "consumer_label": "Exchange rate margin %", "data_type": AttributeDataType.NUMBER, "unit": "%", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "minimum_charge", "label": "Minimum Charge", "consumer_label": "Minimum forex fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_branch", "label": "Available via Branch", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 3, "quality_axis": QualityAxis.AVAILABILITY},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 4, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    }
                ]
            }
        ]
    },

    # B4. Other Operating Income
    {
        "slug": "other-operating-income",
        "name": "Other Operating Income",
        "synonyms": ["miscellaneous income", "other revenue"],
        "subcategories": [
            {
                "slug": "digital-fees",
                "name": "Digital Banking Fees",
                "synonyms": ["digital banking fees", "channel fees", "mobile banking fees"],
                "revenue_lines": [
                    {
                        "slug": "mobile-banking-fees",
                        "name": "Mobile Banking Fees",
                        "channel": "mobile_banking",
                        "fields": [
                            {"key": "registration_fee", "label": "Registration Fee", "consumer_label": "One-time signup cost", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "monthly_fee", "label": "Monthly Fee", "consumer_label": "Monthly maintenance cost", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "per_transaction_fee", "label": "Per Transaction Fee", "consumer_label": "Fee per transaction", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3, "quality_axis": QualityAxis.VALUE},
                            {"key": "ussd_code", "label": "USSD Code", "consumer_label": "Dial code", "data_type": AttributeDataType.STRING, "unit": None, "sort_order": 4, "is_comparable": False},
                            {"key": "available_via_mobile", "label": "Available via Mobile", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 5, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    },
                    {
                        "slug": "internet-banking-fees",
                        "name": "Internet Banking Fees",
                        "channel": "internet_banking",
                        "fields": [
                            {"key": "registration_fee", "label": "Registration Fee", "consumer_label": "One-time setup fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "monthly_fee", "label": "Monthly Fee", "consumer_label": "Monthly platform access fee", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "per_transaction_fee", "label": "Per Transaction Fee", "consumer_label": "Fee per transaction", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 3, "quality_axis": QualityAxis.VALUE},
                            {"key": "available_via_internet", "label": "Available via Internet", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 4, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    }
                ]
            }
        ]
    },

    # B5. Operating Expenses
    {
        "slug": "operating-expenses",
        "name": "Operating Expenses",
        "synonyms": ["costs", "operational costs"],
        "subcategories": [
            {
                "slug": "branch-costs",
                "name": "Branch Costs",
                "synonyms": ["branch fees", "access costs"],
                "revenue_lines": [
                    {
                        "slug": "branch-transaction-fees",
                        "name": "Branch Transaction Fees",
                        "channel": "branch",
                        "fields": [
                            {"key": "cash_deposit", "label": "Cash Deposit Fee", "consumer_label": "Fee to deposit cash", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "cash_withdrawal", "label": "Cash Withdrawal Fee", "consumer_label": "Fee to withdraw cash", "data_type": AttributeDataType.NUMBER, "unit": "USD", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                            {"key": "branch_count", "label": "Branch Count", "consumer_label": "Number of branches", "data_type": AttributeDataType.NUMBER, "unit": "branches", "sort_order": 3},
                            {"key": "available_via_branch", "label": "Available via Branch", "consumer_label": None, "data_type": AttributeDataType.BOOLEAN, "unit": None, "sort_order": 4, "quality_axis": QualityAxis.AVAILABILITY},
                        ]
                    }
                ]
            }
        ]
    },

    # B6. Provisions & Write-offs
    {
        "slug": "provisions-writeoffs",
        "name": "Provisions & Write-offs",
        "synonyms": ["loan loss provisions", "impairment charges"],
        "subcategories": [
            {
                "slug": "loan-loss-provisions",
                "name": "Loan Loss Provisions",
                "synonyms": ["provisioning", "impairment"],
                "revenue_lines": [
                    {
                        "slug": "provision-ratio",
                        "name": "Provision Ratio",
                        "channel": None,
                        "fields": [
                            {"key": "provision_ratio", "label": "Provision Ratio", "consumer_label": "Loan loss provision %", "data_type": AttributeDataType.NUMBER, "unit": "%", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "npl_ratio", "label": "NPL Ratio", "consumer_label": "Non-performing loans %", "data_type": AttributeDataType.NUMBER, "unit": "%", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                        ]
                    }
                ]
            }
        ]
    },

    # B7. Capital & Reserves
    {
        "slug": "capital-reserves",
        "name": "Capital & Reserves",
        "synonyms": ["capital adequacy", "bank capital", "reserves"],
        "subcategories": [
            {
                "slug": "capital-adequacy",
                "name": "Capital Adequacy",
                "synonyms": ["capital ratio", "CAR"],
                "revenue_lines": [
                    {
                        "slug": "capital-ratio",
                        "name": "Capital Adequacy Ratio",
                        "channel": None,
                        "fields": [
                            {"key": "car_ratio", "label": "Capital Ratio", "consumer_label": "Capital adequacy %", "data_type": AttributeDataType.NUMBER, "unit": "%", "sort_order": 1, "quality_axis": QualityAxis.VALUE},
                            {"key": "tier1_ratio", "label": "Tier 1 Ratio", "consumer_label": "Core capital %", "data_type": AttributeDataType.NUMBER, "unit": "%", "sort_order": 2, "quality_axis": QualityAxis.VALUE},
                        ]
                    }
                ]
            }
        ]
    }
]


def seed_banking_sector(db=None):
    """Seed the entire banking ecosystem: 23 banks, flat categories, fee tree, and directory listings."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        print("[Banking Seed] Starting Banking Sector database seed...")

        # 1. Ensure Banking sector exists and is LIVE
        sector = db.query(SectorConfig).filter(SectorConfig.slug == "banking").first()
        if not sector:
            sector = SectorConfig(
                id=_uid(),
                name="Banking",
                slug="banking",
                status=SectorStatus.LIVE,
                icon="building-2",
                blurb="Compare bank fees, accounts, loans and channel networks"
            )
            db.add(sector)
            db.flush()
            print("  [+] Created Sector: Banking")
        else:
            sector.status = SectorStatus.LIVE
            db.flush()

        # 2. Seed 23 Bank Providers
        provider_map = {}
        for b_data in BANK_PROVIDERS:
            provider = db.query(Provider).filter(Provider.name == b_data["name"]).first()
            if not provider:
                provider = Provider(
                    id=_uid(),
                    name=b_data["name"],
                    website_url=b_data["website_url"],
                    corporate_domain=b_data["corporate_domain"],
                    description=f"{b_data['name']} ({b_data['bank_type'].title()})",
                    verified=True
                )
                db.add(provider)
                db.flush()
                print(f"  [+] Bank Provider: {provider.name}")
            else:
                provider.website_url = b_data["website_url"]
                provider.corporate_domain = b_data["corporate_domain"]
                db.flush()
            provider_map[b_data["name"]] = provider

        # 3. Seed PART A: Flat Consumer Banking Categories
        print("  [*] Seeding PART A: Flat Consumer Banking Categories...")
        cat_map = {}
        for cat_spec in FLAT_BANKING_CATEGORIES:
            cat = db.query(Category).filter(
                Category.sector_id == sector.id,
                Category.slug == cat_spec["slug"]
            ).first()

            if not cat:
                cat = Category(
                    id=_uid(),
                    sector_id=sector.id,
                    name=cat_spec["name"],
                    slug=cat_spec["slug"],
                    level=CategoryLevel.STANDARD,
                    parent_id=None,
                    channel=None
                )
                cat.synonyms = cat_spec.get("synonyms", [])
                db.add(cat)
                db.flush()
                print(f"    [+] Flat Category: {cat.name} ({cat.slug})")
            else:
                cat.synonyms = cat_spec.get("synonyms", [])
                cat.level = CategoryLevel.STANDARD

            cat_map[cat_spec["slug"]] = cat

            # Upsert schema fields
            for f in cat_spec.get("fields", []):
                attr = db.query(AttributeSchemaField).filter(
                    AttributeSchemaField.category_id == cat.id,
                    AttributeSchemaField.key == f["key"]
                ).first()

                if not attr:
                    attr = AttributeSchemaField(
                        id=_uid(),
                        category_id=cat.id,
                        key=f["key"],
                        label=f["label"],
                        consumer_label=f.get("consumer_label"),
                        data_type=f.get("data_type", AttributeDataType.NUMBER),
                        unit=f.get("unit"),
                        sort_order=f.get("sort_order", 0),
                        quality_axis=f.get("quality_axis"),
                        is_comparable=f.get("is_comparable", True)
                    )
                    db.add(attr)
                else:
                    attr.label = f["label"]
                    attr.consumer_label = f.get("consumer_label")
                    attr.data_type = f.get("data_type", AttributeDataType.NUMBER)
                    attr.unit = f.get("unit")
                    attr.sort_order = f.get("sort_order", 0)
                    attr.quality_axis = f.get("quality_axis")
                    attr.is_comparable = f.get("is_comparable", True)

        # 4. Seed PART B: 3-Level Banking Fee Hierarchy
        print("  [*] Seeding PART B: 3-Level Banking Fee Hierarchy...")
        for fee_cat in BANKING_FEE_HIERARCHY:
            # 1. Level: fee_category (parent_id = None)
            fc = db.query(Category).filter(
                Category.sector_id == sector.id,
                Category.slug == fee_cat["slug"]
            ).first()

            if not fc:
                fc = Category(
                    id=_uid(),
                    sector_id=sector.id,
                    name=fee_cat["name"],
                    slug=fee_cat["slug"],
                    level=CategoryLevel.FEE_CATEGORY,
                    parent_id=None,
                    channel=None
                )
                fc.synonyms = fee_cat.get("synonyms", [])
                db.add(fc)
                db.flush()
                print(f"    [+] [L1 Fee Category] {fc.name} ({fc.slug})")
            else:
                fc.level = CategoryLevel.FEE_CATEGORY
                fc.synonyms = fee_cat.get("synonyms", [])
                fc.parent_id = None

            for sub_cat in fee_cat.get("subcategories", []):
                # 2. Level: subcategory (parent_id = fc.id)
                sc = db.query(Category).filter(
                    Category.sector_id == sector.id,
                    Category.slug == sub_cat["slug"]
                ).first()

                if not sc:
                    sc = Category(
                        id=_uid(),
                        sector_id=sector.id,
                        name=sub_cat["name"],
                        slug=sub_cat["slug"],
                        level=CategoryLevel.SUBCATEGORY,
                        parent_id=fc.id,
                        channel=None
                    )
                    sc.synonyms = sub_cat.get("synonyms", [])
                    db.add(sc)
                    db.flush()
                    print(f"      [+] [L2 Subcategory] {sc.name} ({sc.slug})")
                else:
                    sc.level = CategoryLevel.SUBCATEGORY
                    sc.synonyms = sub_cat.get("synonyms", [])
                    sc.parent_id = fc.id

                for rev_line in sub_cat.get("revenue_lines", []):
                    # 3. Level: revenue_line (parent_id = sc.id, channel = rev_line.channel)
                    rl = db.query(Category).filter(
                        Category.sector_id == sector.id,
                        Category.slug == rev_line["slug"]
                    ).first()

                    if not rl:
                        rl = Category(
                            id=_uid(),
                            sector_id=sector.id,
                            name=rev_line["name"],
                            slug=rev_line["slug"],
                            level=CategoryLevel.REVENUE_LINE,
                            parent_id=sc.id,
                            channel=rev_line.get("channel")
                        )
                        db.add(rl)
                        db.flush()
                        print(f"        [+] [L3 Revenue Line] {rl.name} ({rl.slug}) [Channel: {rl.channel}]")
                    else:
                        rl.level = CategoryLevel.REVENUE_LINE
                        rl.parent_id = sc.id
                        rl.channel = rev_line.get("channel")

                    # Upsert schema fields for revenue_line
                    for f in rev_line.get("fields", []):
                        attr = db.query(AttributeSchemaField).filter(
                            AttributeSchemaField.category_id == rl.id,
                            AttributeSchemaField.key == f["key"]
                        ).first()

                        if not attr:
                            attr = AttributeSchemaField(
                                id=_uid(),
                                category_id=rl.id,
                                key=f["key"],
                                label=f["label"],
                                consumer_label=f.get("consumer_label"),
                                data_type=f.get("data_type", AttributeDataType.NUMBER),
                                unit=f.get("unit"),
                                sort_order=f.get("sort_order", 0),
                                quality_axis=f.get("quality_axis"),
                                is_comparable=True
                            )
                            db.add(attr)
                        else:
                            attr.label = f["label"]
                            attr.consumer_label = f.get("consumer_label")
                            attr.data_type = f.get("data_type", AttributeDataType.NUMBER)
                            attr.unit = f.get("unit")
                            attr.sort_order = f.get("sort_order", 0)
                            attr.quality_axis = f.get("quality_axis")
                            attr.is_comparable = True

        # 5. Populate Bank Directory Listings under category 'banks' (A4)
        print("  [*] Populating Bank Directory Listings (A4 'banks')...")
        banks_cat = cat_map.get("banks")
        if banks_cat:
            now = datetime.utcnow()
            for b in BANK_PROVIDERS:
                provider = provider_map[b["name"]]
                channels = b["channels"]
                channel_count = sum(1 for v in channels.values() if v is True)

                listing_name = f"{b['name']} Banking & Channels"
                listing = db.query(Listing).filter(
                    Listing.category_id == banks_cat.id,
                    Listing.provider_id == provider.id,
                    Listing.name == listing_name
                ).first()

                attrs = {
                    "bank_type": b["bank_type"],
                    "ussd_code": b["ussd_code"],
                    "ussd_brand": b["ussd_brand"],
                    "channel_count": channel_count,
                    **channels
                }

                if not listing:
                    listing = Listing(
                        id=_uid(),
                        category_id=banks_cat.id,
                        provider_id=provider.id,
                        name=listing_name,
                        description=f"Official digital and physical banking channels for {b['name']}.",
                        price=0.00,
                        currency="USD",
                        source_url=b["website_url"],
                        status=ListingStatus.PUBLISHED,
                        freshness_status=FreshnessStatus.UNVERIFIED,
                        last_update_source=ListingUpdateSource.SCRAPER,
                        last_verified_at=now
                    )
                    listing.attributes = attrs
                    db.add(listing)
                    db.flush()

                    hist = ListingPriceHistory(
                        id=_uid(),
                        listing_id=listing.id,
                        price=0.00,
                        currency="USD",
                        recorded_at=now
                    )
                    db.add(hist)
                else:
                    listing.attributes = attrs
                    listing.source_url = b["website_url"]
                    listing.last_verified_at = now
                    listing.last_update_source = ListingUpdateSource.SCRAPER

        db.commit()
        print("[Banking Seed] Successfully seeded all 23 Zimbabwean banks, flat categories, and the 3-level fee hierarchy!")
    except Exception as e:
        db.rollback()
        print(f"[Banking Seed] ERROR: {e}")
        raise
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    from datetime import datetime
    seed_banking_sector()
else:
    from datetime import datetime
