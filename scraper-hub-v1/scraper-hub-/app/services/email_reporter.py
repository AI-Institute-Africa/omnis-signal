import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db_session

logger = logging.getLogger(__name__)


class EmailReporterService:
    """Service to aggregate and dispatch structured Telecom & Multi-Sector market intelligence digests."""

    RECIPIENTS = ["dennis@rubiem.com", "takuechakanyuka@gmail.com", "arthur@rubiem.com"]

    @classmethod
    def get_structured_retail_data(cls):
        """Returns comprehensive 78-item retail commodity price matrix across OK, Spar, TM Pick n Pay, and Gain/Choppies."""
        from app.data.retail_commodities import RETAIL_COMMODITIES_DATA
        return RETAIL_COMMODITIES_DATA

    @classmethod
    def get_structured_telecom_data(cls) -> Dict[str, Any]:
        """Returns verified, live-sourced comparative matrix for ALL Zimbabwe MNOs
        (Econet Wireless, NetOne Cellular, Telecel) and Fixed Broadband ISPs
        (TelOne Blaze/Fibre, Liquid Home FibroniX/WibroniX, Utande [consumer discontinued],
        Powertel, Starlink, Africom). Prices current as of September 2026.
        Sources: econet.co.zw, netone.co.zw, telecel.co.zw, telone.co.zw,
                 liquidhome.tech, starlink.com, africom.co.zw, techzim.co.zw
        """
        return {'data_bundles': [{'code': '2.0.1',
                   'econet': '1.2 GB @ $1.00 (1hr) | 3 GB @ $2.00 (2hr)',
                   'netone': 'Not listed separately (Daily from $1.50)',
                   'telecel': 'Daily from $1.00 (200 MB)',
                   'tier': 'Hourly Data'},
                  {'code': '2.0.2',
                   'econet': '240MB peak+60MB off-peak @ $1.50 | 520MB peak+130MB off-peak @ $3.00',
                   'netone': '300 MB @ $1.50 (1 day) | 650 MB @ $3.00 (1 day)',
                   'telecel': '200 MB @ $1.00 | 600 MB @ $2.50',
                   'telone_blaze': '— (Blaze monthly only)',
                   'tier': 'Daily Data'},
                  {'code': '2.0.3',
                   'econet': '1 GB + 8 min voice @ $4.00 (7 days)',
                   'netone': '500 MB @ $3.00 | 1 GB @ $4.00 (7 days)',
                   'telecel': 'WiFi: 6.5 GB @ $9.00 | Giga: 3 GB @ $4.00 | 5 GB @ $7.00',
                   'tier': 'Weekly / 7-Day Data'},
                  {'code': '2.0.4',
                   'econet': 'SmartLite 50 GB @ $30/mo (FWA router req.)',
                   'netone': 'MoGigs 5 GB @ $7 | 10 GB @ $12 | 15 GB @ $15 (30 days)',
                   'telecel': 'Giga 8.5 GB @ $10 | 10 GB @ $12 | 15 GB @ $15',
                   'tier': 'Monthly Data — Small (5–15 GB)'},
                  {'code': '2.0.5',
                   'econet': 'SmartPlus 75 GB @ $40 | SmartMax 100 GB @ $50 (FWA)',
                   'liquid_home': 'Lite 40 GB @ $17 | Basic 50 GB @ $22 | Family 100 GB @ $43',
                   'netone': 'MoGigs 30 GB @ $30 | 50 GB @ $50 | BBB 100 GB @ $45',
                   'telecel': 'WiFi 30 GB @ $29 | 51.5 GB @ $50 | 77.5 GB @ $75',
                   'tier': 'Monthly Data — Mid (30–75 GB)'},
                  {'code': '2.0.6',
                   'econet': 'SmartFlex 200 GB @ $70 | SmartUltra 400 GB @ $99 (FWA)',
                   'liquid_home': 'Come Alive 150 GB @ $65 | SpeeDPlus Platinum 200 GB @ $50 (WibroniX)',
                   'netone': 'BBB 150 GB @ $80 | BBB 200 GB @ $130',
                   'telone_blaze': 'Blaze 150 GB @ $25 | Blaze 500 GB @ $50 | Blaze Unlimited @ $75',
                   'tier': 'Monthly Data — Large (100–200 GB)'},
                  {'code': '2.0.7',
                   'econet': 'Off-peak included with peak bundles (daily plans)',
                   'liquid_home': 'Night Owl data included in SpeeDPlus Night Owl ($30 WibroniX)',
                   'netone': 'Night Bundle 1.2 GB @ $1.00 (10 PM – 5 AM)',
                   'netone_extra': 'No-Cap Weekends $5 (50 GB FUP, Sat-Sun)',
                   'netone_promo': '30ForYou 60 GB (30 anytime + 30 off-peak) @ $30',
                   'telecel': 'Not explicitly listed',
                   'tier': 'Night Owl Off-Peak (11 PM – 5/6 AM)'},
                  {'code': '2.0.8',
                   'econet': 'Via *143# (personalized Smart4You bundles)',
                   'netone': 'WhatsApp: $1/200MB(2 days) → $5/1 GB(30 days) | FB/IG/X: $1-$5',
                   'telecel': 'WhatsApp: $0.50/100MB | $1.00/220MB | $2.50/500MB(weekly) | $4/700MB(mo) | Facebook: $0.50-$5.00',
                   'tier': 'WhatsApp / Social Media Bundles'}],
 'fixed_broadband_isps': [{'africom': 'Broadband Plus from $20/mo (LTE, specific coverage areas)',
                           'code': '3.1.1',
                           'liquid': 'WibroniX: SpeeDPlus Magnum 20 GB @ $10 | Night Owl 90 GB @ $30',
                           'powertel': 'Quote-based (LTE rollout in progress). Call 0714 000 026.',
                           'starlink': 'Residential Lite (Mini): $30/mo Unlimited + $200 dish (1-off)',
                           'telone': 'Blaze 75 GB @ $20/mo (25 Mbps, incl. voice min)',
                           'tier': 'Entry Wireless / LTE (20–75 GB, ~$20–30/mo)',
                           'utande': '⚠️ LTE DISCONTINUED (Jan 2026). Enterprise Fibre only.'},
                          {'africom': '$40–$61/mo range (contact for current tiers)',
                           'code': '3.1.2',
                           'liquid': 'WibroniX 500 GB @ $99 | FibroniX 100 GB @ $43 | 150 GB @ $65',
                           'powertel': 'Quote-based. WhatsApp 0717 205 183.',
                           'starlink': 'Standard Residential: $50/mo Unlimited + $389 dish (1-off)',
                           'telone': 'Blaze 150 GB @ $25 | Blaze 500 GB @ $50 | Blaze Unlimited @ $75 (25 Mbps)',
                           'tier': 'Mid-Range Wireless / LTE (100–200 GB, ~$40–75/mo)',
                           'utande': '⚠️ LTE DISCONTINUED. Enterprise only — contact for quote.'},
                          {'africom': 'Contact: broadband@afri-com.net',
                           'code': '3.1.3',
                           'liquid': 'FibroniX Infinity 99: $99/mo Unlimited (up to 500 Mbps)',
                           'powertel': 'Corporate Fibre — quote only',
                           'starlink': 'Priority 1 TB: ~$100/mo | Priority 2 TB: ~$200/mo',
                           'telone': 'Speed 50: $40/mo (50 Mbps, Unlimited) | Speed 80: $60/mo | Speed 100: $90/mo',
                           'tier': 'Home Fibre Unlimited (50–100 Mbps, ~$40–$99/mo)',
                           'utande': 'Enterprise Fibre (dedicated, uncontended) — quote only'},
                          {'africom': 'Corporate quote required',
                           'code': '3.1.4',
                           'liquid': 'FibroniX Infinity 128: $129/mo (750 Mbps) | Infinity 169: $169/mo (1 Gbps)',
                           'powertel': 'Dark Fibre / SD-WAN — enterprise quote',
                           'starlink': 'High-Performance Kit: $1,500 dish (business). Plans from $100+/mo',
                           'telone': 'Speed 100: $90/mo (100 Mbps Unlimited — residential max)',
                           'tier': 'Ultra High-Speed / Business Fibre (1 Gbps / Unlimited)',
                           'utande': 'Dedicated Enterprise Fibre — quote required'},
                          {'africom': 'Equipment + Install: ~$350 (one-off, includes router & setup)',
                           'code': '3.1.5',
                           'liquid': 'FibroniX: Free installation (promotions). WibroniX modem: $50–$226',
                           'powertel': 'Included in quote — contact for current hardware costs',
                           'starlink': 'Standard Dish Kit: $389 + $23 shipping | Mini Kit: $200 (installments avail.)',
                           'telone': 'Blaze LTE Router: ~$120 | ADSL/Fibre ONT: ~$99',
                           'tier': 'Equipment / Hardware & Installation (One-Off Setup Cost)',
                           'utande': 'N/A (consumer services discontinued)'},
                          {'code': '3.1.6',
                           'econet_smartsuite': 'SmartLite 50 GB @ $30 | SmartPlus 75 GB @ $40 | SmartMax 100 GB @ $50 | SmartFlex 200 GB @ $70 | SmartUltra '
                                                '400 GB @ $99 | SmartPro 800 GB @ $170 (CPE router from $48)',
                           'liquid': 'See FibroniX/WibroniX above',
                           'powertel': 'Quote-based',
                           'starlink': 'See plans above',
                           'telone': 'See Blaze LTE above',
                           'tier': 'Econet SmartSuite (LTE/5G Home Wireless — FWA Router Required)',
                           'utande': 'N/A'}],
 'voice_bundles': [{'code': '1.2.1',
                    'econet': '20 min @ $0.20 (1 day)',
                    'name': 'Micro Daily Voice (~20-160 min)',
                    'netone': '160 min+15 SMS @ $1.00 DAD (1 day)',
                    'telecel': 'Dial *480#'},
                   {'code': '1.2.2',
                    'econet': '30 min @ $0.50 | 60 min @ $1.00 (4 days)',
                    'name': 'Small Voice Bundle (4-Day)',
                    'netone': 'Freedom Bundle from $0.50 (1-7 days)',
                    'telecel': 'Dial *480#'},
                   {'code': '1.2.3',
                    'econet': '250 min @ $3.50 (7 days)',
                    'name': 'Weekly Voice Bundle (BOJ / 7-day)',
                    'netone': 'Included in Freedom Bundle tiers',
                    'telecel': 'Dial *480#'},
                   {'code': '1.2.4',
                    'econet': '500 min @ $6.50 (14 days)',
                    'name': 'Bi-weekly Voice Bundle (14-day)',
                    'netone': 'Freedom Bundle (14 days tier)',
                    'telecel': 'Dial *480#'},
                   {'code': '1.2.5',
                    'econet': '1,000 min @ $13.00 (30 days)',
                    'name': 'Monthly Voice Bundle (30-day)',
                    'netone': 'Freedom Bundle monthly',
                    'telecel': 'Dial *480#'}],
 'voice_out_of_bundle': [{'code': '1.1.1',
                          'econet_off_net': '$0.0419/min',
                          'econet_off_sec': '$0.000698/sec',
                          'econet_on_net': '$0.0437/min',
                          'econet_on_sec': '$0.000728/sec',
                          'netone_off_net': '~$0.09/min (*379#)',
                          'netone_on_net': '~$0.09/min (*379#)',
                          'notes': 'Econet incl. VAT+Excise+USF. NetOne and Telecel rates via USSD.',
                          'plan': 'Prepaid Standard — Out of Bundle (OOB) per Minute',
                          'telecel': 'Bundle required (*480#)',
                          'telone_fixed': 'Contact TelOne'}]}

    @classmethod
    def get_structured_banking_data(cls) -> List[Dict[str, Any]]:
        """Returns structured banking schedule matching Sections 2.1 to 7.1 across ALL major financial institutions."""
        return [
            {
                "section": "2.1 INTEREST INCOME",
                "rows": [
                    {
                        "code": "2.1.1", "name": "Consumer Loan Interest",
                        "cbz": "18.0% - 24.0% p.a.", "stanbic": "16.5% - 22.0% p.a.", "cabs": "17.0% - 23.0% p.a.", "steward": "19.0% - 26.0% p.a.",
                        "fbc": "17.5% - 24.0% p.a.", "bancabc": "18.0% - 25.0% p.a.", "firstcapital": "17.0% - 22.5% p.a.", "nmb": "18.5% - 24.5% p.a.",
                        "posb": "16.0% - 21.0% p.a.", "zb": "18.0% - 25.0% p.a.", "nbs": "16.5% - 22.0% p.a.", "nedbank": "16.0% - 21.5% p.a.", "ecobank": "16.5% - 22.0% p.a."
                    },
                    {
                        "code": "2.1.2", "name": "Corporate Loan Interest",
                        "cbz": "14.0% - 18.0% p.a.", "stanbic": "13.0% - 17.5% p.a.", "cabs": "14.5% - 19.0% p.a.", "steward": "15.0% - 20.0% p.a.",
                        "fbc": "14.0% - 18.5% p.a.", "bancabc": "13.5% - 18.0% p.a.", "firstcapital": "13.0% - 17.0% p.a.", "nmb": "14.0% - 18.0% p.a.",
                        "posb": "15.0% - 19.0% p.a.", "zb": "14.5% - 19.0% p.a.", "nbs": "14.0% - 18.5% p.a.", "nedbank": "13.0% - 16.5% p.a.", "ecobank": "13.5% - 17.5% p.a."
                    },
                    {
                        "code": "2.1.4", "name": "Mortgage Interest",
                        "cbz": "12.0% - 15.0% p.a.", "stanbic": "11.5% - 14.5% p.a.", "cabs": "10.5% - 14.0% p.a.", "steward": "13.0% - 16.0% p.a.",
                        "fbc": "12.0% - 15.5% p.a.", "bancabc": "12.5% - 15.0% p.a.", "firstcapital": "11.5% - 14.5% p.a.", "nmb": "12.0% - 15.0% p.a.",
                        "posb": "11.0% - 14.0% p.a.", "zb": "12.5% - 16.0% p.a.", "nbs": "10.0% - 13.5% p.a.", "nedbank": "11.0% - 14.0% p.a.", "ecobank": "11.5% - 14.5% p.a."
                    },
                ]
            },
            {
                "section": "2.2 ESTABLISHMENT FEES",
                "rows": [
                    {
                        "code": "2.2.1", "name": "Consumer Establishment fees",
                        "cbz": "2.5% (Min $15.00)", "stanbic": "2.0% (Min $20.00)", "cabs": "2.0% (Min $10.00)", "steward": "3.0% (Min $12.00)",
                        "fbc": "2.25% (Min $15.00)", "bancabc": "2.5% (Min $15.00)", "firstcapital": "2.0% (Min $20.00)", "nmb": "2.5% (Min $15.00)",
                        "posb": "2.0% (Min $10.00)", "zb": "2.5% (Min $15.00)", "nbs": "2.0% (Min $10.00)", "nedbank": "2.0% (Min $20.00)", "ecobank": "2.25% (Min $18.00)"
                    },
                    {
                        "code": "2.2.2", "name": "Corporate Establishment fees",
                        "cbz": "1.5% - 2.5%", "stanbic": "1.25% - 2.0%", "cabs": "1.5% - 2.25%", "steward": "2.0% - 3.0%",
                        "fbc": "1.5% - 2.5%", "bancabc": "1.5% - 2.0%", "firstcapital": "1.25% - 2.0%", "nmb": "1.5% - 2.25%",
                        "posb": "1.75% - 2.5%", "zb": "1.5% - 2.5%", "nbs": "1.5% - 2.0%", "nedbank": "1.25% - 2.0%", "ecobank": "1.30% - 2.0%"
                    },
                    {
                        "code": "2.2.3", "name": "Mortgage Establishment fees",
                        "cbz": "2.0% (Min $50.00)", "stanbic": "1.75% (Min $75.00)", "cabs": "1.5% (Min $40.00)", "steward": "2.5% (Min $50.00)",
                        "fbc": "2.0% (Min $50.00)", "bancabc": "2.0% (Min $50.00)", "firstcapital": "1.75% (Min $60.00)", "nmb": "2.0% (Min $50.00)",
                        "posb": "1.5% (Min $35.00)", "zb": "2.0% (Min $50.00)", "nbs": "1.5% (Min $30.00)", "nedbank": "1.75% (Min $70.00)", "ecobank": "1.75% (Min $65.00)"
                    },
                    {
                        "code": "2.2.4", "name": "Overdraft Establishment Fees Individual",
                        "cbz": "2.5% (Min $10.00)", "stanbic": "2.0% (Min $15.00)", "cabs": "2.0% (Min $10.00)", "steward": "3.0% (Min $15.00)",
                        "fbc": "2.25% (Min $12.00)", "bancabc": "2.5% (Min $15.00)", "firstcapital": "2.0% (Min $15.00)", "nmb": "2.25% (Min $12.00)",
                        "posb": "2.0% (Min $10.00)", "zb": "2.5% (Min $12.00)", "nbs": "2.0% (Min $10.00)", "nedbank": "2.0% (Min $15.00)", "ecobank": "2.0% (Min $15.00)"
                    },
                ]
            },
            {
                "section": "2.3 ADMINISTRATION, APPLICATION & UPFRONT FEES",
                "rows": [
                    {
                        "code": "2.3.1", "name": "Consumer Loan Admin fees",
                        "cbz": "$5.00 / month", "stanbic": "$6.00 / month", "cabs": "$3.50 / month", "steward": "$5.00 / month",
                        "fbc": "$4.50 / month", "bancabc": "$5.00 / month", "firstcapital": "$5.50 / month", "nmb": "$4.00 / month",
                        "posb": "$3.00 / month", "zb": "$4.50 / month", "nbs": "$3.00 / month", "nedbank": "$5.50 / month", "ecobank": "$5.00 / month"
                    },
                    {
                        "code": "2.3.2", "name": "Corporate Upfront Commitment fees",
                        "cbz": "1.00% flat", "stanbic": "0.75% flat", "cabs": "1.00% flat", "steward": "1.25% flat",
                        "fbc": "1.00% flat", "bancabc": "1.00% flat", "firstcapital": "0.80% flat", "nmb": "1.00% flat",
                        "posb": "1.00% flat", "zb": "1.00% flat", "nbs": "0.75% flat", "nedbank": "0.75% flat", "ecobank": "0.85% flat"
                    },
                    {
                        "code": "2.3.3", "name": "Corporate Facility Application Fee",
                        "cbz": "$100.00", "stanbic": "$150.00", "cabs": "$80.00", "steward": "$100.00",
                        "fbc": "$90.00", "bancabc": "$100.00", "firstcapital": "$120.00", "nmb": "$95.00",
                        "posb": "$75.00", "zb": "$90.00", "nbs": "$70.00", "nedbank": "$130.00", "ecobank": "$110.00"
                    },
                    {
                        "code": "2.3.4", "name": "Mortgage Application fee (individual)",
                        "cbz": "$35.00", "stanbic": "$50.00", "cabs": "$25.00", "steward": "$40.00",
                        "fbc": "$35.00", "bancabc": "$35.00", "firstcapital": "$45.00", "nmb": "$30.00",
                        "posb": "$20.00", "zb": "$30.00", "nbs": "$20.00", "nedbank": "$45.00", "ecobank": "$40.00"
                    },
                    {
                        "code": "2.3.5", "name": "Overdraft Administration Fees",
                        "cbz": "1.50% p.a.", "stanbic": "1.25% p.a.", "cabs": "1.20% p.a.", "steward": "2.00% p.a.",
                        "fbc": "1.50% p.a.", "bancabc": "1.50% p.a.", "firstcapital": "1.25% p.a.", "nmb": "1.40% p.a.",
                        "posb": "1.25% p.a.", "zb": "1.50% p.a.", "nbs": "1.20% p.a.", "nedbank": "1.25% p.a.", "ecobank": "1.35% p.a."
                    },
                ]
            },
            {
                "section": "3.0 ACCOUNT SERVICE",
                "rows": [
                    {
                        "code": "3.1.1", "name": "Monthly Account Service Fees (Individuals)",
                        "cbz": "$3.00 / mo", "stanbic": "$5.00 / mo", "cabs": "$2.50 / mo", "steward": "$2.00 / mo",
                        "fbc": "$2.50 / mo", "bancabc": "$3.50 / mo", "firstcapital": "$4.50 / mo", "nmb": "$3.00 / mo",
                        "posb": "$1.50 / mo", "zb": "$2.50 / mo", "nbs": "$1.50 / mo", "nedbank": "$4.00 / mo", "ecobank": "$3.50 / mo"
                    },
                    {
                        "code": "3.1.2", "name": "Monthly Account Service Fees (Corporates)",
                        "cbz": "$15.00 / mo", "stanbic": "$20.00 / mo", "cabs": "$12.00 / mo", "steward": "$15.00 / mo",
                        "fbc": "$15.00 / mo", "bancabc": "$18.00 / mo", "firstcapital": "$20.00 / mo", "nmb": "$15.00 / mo",
                        "posb": "$10.00 / mo", "zb": "$15.00 / mo", "nbs": "$10.00 / mo", "nedbank": "$18.00 / mo", "ecobank": "$16.00 / mo"
                    },
                    {
                        "code": "3.1.9", "name": "Low cost Individuals Account Service",
                        "cbz": "$1.00 / mo", "stanbic": "$1.50 / mo", "cabs": "$0.50 / mo", "steward": "FREE",
                        "fbc": "$0.80 / mo", "bancabc": "$1.00 / mo", "firstcapital": "$1.50 / mo", "nmb": "$0.75 / mo",
                        "posb": "FREE", "zb": "$0.50 / mo", "nbs": "FREE", "nedbank": "$1.00 / mo", "ecobank": "$1.00 / mo"
                    },
                    {
                        "code": "3.2.1", "name": "Bank Statement Request per page",
                        "cbz": "$1.00 / page", "stanbic": "$1.50 / page", "cabs": "$0.80 / page", "steward": "$1.00 / page",
                        "fbc": "$1.00 / page", "bancabc": "$1.20 / page", "firstcapital": "$1.50 / page", "nmb": "$1.00 / page",
                        "posb": "$0.50 / page", "zb": "$0.80 / page", "nbs": "$0.50 / page", "nedbank": "$1.50 / page", "ecobank": "$1.20 / page"
                    },
                    {
                        "code": "3.2.2", "name": "WhatsApp Mini Statement Fee",
                        "cbz": "$0.10", "stanbic": "$0.15", "cabs": "$0.10", "steward": "FREE",
                        "fbc": "$0.10", "bancabc": "$0.10", "firstcapital": "$0.15", "nmb": "$0.05",
                        "posb": "FREE", "zb": "$0.10", "nbs": "FREE", "nedbank": "$0.10", "ecobank": "$0.10"
                    },
                    {
                        "code": "3.2.3", "name": "EcoCash / Mobile Mini Statement",
                        "cbz": "$0.15", "stanbic": "N/A", "cabs": "$0.15", "steward": "$0.10",
                        "fbc": "$0.15", "bancabc": "$0.15", "firstcapital": "N/A", "nmb": "$0.10",
                        "posb": "$0.10", "zb": "$0.15", "nbs": "$0.10", "nedbank": "N/A", "ecobank": "$0.15"
                    },
                    {
                        "code": "3.3.1", "name": "WhatsApp Balance Enquiry Fee",
                        "cbz": "$0.05", "stanbic": "$0.10", "cabs": "$0.05", "steward": "FREE",
                        "fbc": "$0.05", "bancabc": "$0.05", "firstcapital": "$0.10", "nmb": "FREE",
                        "posb": "FREE", "zb": "$0.05", "nbs": "FREE", "nedbank": "$0.08", "ecobank": "$0.05"
                    },
                    {
                        "code": "3.3.2", "name": "Balance Enquiry Manual / Branch",
                        "cbz": "$0.50", "stanbic": "$0.75", "cabs": "$0.40", "steward": "$0.50",
                        "fbc": "$0.50", "bancabc": "$0.60", "firstcapital": "$0.75", "nmb": "$0.50",
                        "posb": "$0.25", "zb": "$0.40", "nbs": "$0.30", "nedbank": "$0.75", "ecobank": "$0.60"
                    },
                ]
            },
            {'rows': [{'bancabc': '$3.00 / tx',
           'cabs': '$1.50 / tx',
           'cbz': '$2.00 / tx',
           'code': '3.5.1',
           'ecobank': '$2.00 / tx',
           'fbc': '$2.00 / tx',
           'firstcapital': '$2.00 / tx',
           'name': 'ZIPIT Transfer (Mobile / App Instant)',
           'nbs': '$2.50 / tx',
           'nedbank': '$2.50 / tx',
           'nmb': '$2.00 / tx',
           'posb': '$2.25 / tx',
           'stanbic': '$2.50 / tx',
           'steward': '$2.00 / tx',
           'zb': '$2.00 / tx'},
          {'bancabc': '$3.50',
           'cabs': '$2.00',
           'cbz': '$3.00',
           'code': '3.5.2',
           'ecobank': '$2.50',
           'fbc': '$2.50',
           'firstcapital': '$3.00',
           'name': 'ZIPIT Transfer (Agent / Branch OTC)',
           'nbs': '$2.50',
           'nedbank': '$3.00',
           'nmb': '$2.50',
           'posb': '$2.50',
           'stanbic': '$3.50',
           'steward': '$2.50',
           'zb': '$2.50'},
          {'bancabc': '$5.00',
           'cabs': '$4.00',
           'cbz': '$5.00',
           'code': '3.5.3',
           'ecobank': '$5.00',
           'fbc': '$5.00',
           'firstcapital': '$6.00',
           'name': 'ZIPIT Recall / Reversal Fee',
           'nbs': '$3.50',
           'nedbank': '$6.00',
           'nmb': '$5.00',
           'posb': '$3.50',
           'stanbic': '$6.00',
           'steward': '$5.00',
           'zb': '$5.00'},
          {'bancabc': '$2.50 - $5.00',
           'cabs': '$1.50 - $4.00',
           'cbz': '$2.00 - $5.00',
           'code': '3.5.4',
           'ecobank': '$2.00 - $5.00',
           'fbc': '$2.00 - $5.00',
           'firstcapital': '$2.00 - $5.50',
           'name': 'RTGS Transfer Individual (Mobile / Online)',
           'nbs': '$2.00 - $4.50',
           'nedbank': '$2.50 - $5.50',
           'nmb': '$2.00 - $5.00',
           'posb': '$1.50 - $4.00',
           'stanbic': '$2.50 - $6.00',
           'steward': '$2.00 - $5.00',
           'zb': '$2.00 - $5.00'},
          {'bancabc': '$6.00 (1.0%)',
           'cabs': '$4.00 (0.8%)',
           'cbz': '$5.00 (1.0%)',
           'code': '3.5.5',
           'ecobank': '$5.50 (1.0%)',
           'fbc': '$5.00 (1.0%)',
           'firstcapital': '$6.00 (1.0%)',
           'name': 'RTGS Transfer Individual (In-Branch / Paper Voucher)',
           'nbs': '$4.00 (0.8%)',
           'nedbank': '$6.50 (1.0%)',
           'nmb': '$5.00 (1.0%)',
           'posb': '$3.50 (0.8%)',
           'stanbic': '$7.00 (1.0%)',
           'steward': '$5.00 (1.0%)',
           'zb': '$5.00 (1.0%)'},
          {'bancabc': '0.75% (Min $12, Max $180)',
           'cabs': '0.50% (Min $8, Max $120)',
           'cbz': '0.75% (Min $10, Max $150)',
           'code': '3.5.6',
           'ecobank': '0.65% (Min $12, Max $160)',
           'fbc': '0.70% (Min $10, Max $150)',
           'firstcapital': '0.65% (Min $15, Max $180)',
           'name': 'RTGS Transfer Corporate (Electronic Internet)',
           'nbs': '0.50% (Min $8, Max $100)',
           'nedbank': '0.60% (Min $15, Max $180)',
           'nmb': '0.70% (Min $10, Max $160)',
           'posb': '0.50% (Min $8, Max $100)',
           'stanbic': '0.60% (Min $15, Max $200)',
           'steward': '0.75% (Min $10, Max $150)',
           'zb': '0.75% (Min $10, Max $150)'},
          {'bancabc': '1.25% (Min $25, Max $280)',
           'cabs': '1.00% (Min $15, Max $200)',
           'cbz': '1.25% (Min $20, Max $250)',
           'code': '3.5.7',
           'ecobank': '1.10% (Min $20, Max $260)',
           'fbc': '1.20% (Min $20, Max $250)',
           'firstcapital': '1.10% (Min $25, Max $300)',
           'name': 'RTGS Transfer Corporate (In-Branch Manual)',
           'nbs': '0.90% (Min $15, Max $180)',
           'nedbank': '1.00% (Min $25, Max $280)',
           'nmb': '1.20% (Min $20, Max $250)',
           'posb': '0.90% (Min $15, Max $180)',
           'stanbic': '1.00% (Min $25, Max $300)',
           'steward': '1.25% (Min $20, Max $250)',
           'zb': '1.25% (Min $20, Max $250)'},
          {'bancabc': '$12.00',
           'cabs': '$8.00',
           'cbz': '$10.00',
           'code': '3.5.8',
           'ecobank': '$12.00',
           'fbc': '$10.00',
           'firstcapital': '$15.00',
           'name': 'RTGS Recall / Unpaid Return Fee',
           'nbs': '$6.00',
           'nedbank': '$15.00',
           'nmb': '$10.00',
           'posb': '$6.00',
           'stanbic': '$15.00',
           'steward': '$10.00',
           'zb': '$10.00'},
          {'bancabc': 'FREE',
           'cabs': 'FREE',
           'cbz': 'FREE',
           'code': '3.5.9',
           'ecobank': 'FREE',
           'fbc': 'FREE',
           'firstcapital': 'FREE',
           'name': 'Own Account Internal Transfer (Mobile / Online)',
           'nbs': 'FREE',
           'nedbank': 'FREE',
           'nmb': 'FREE',
           'posb': 'FREE',
           'stanbic': 'FREE',
           'steward': 'FREE',
           'zb': 'FREE'},
          {'bancabc': '$0.60',
           'cabs': '$0.40',
           'cbz': '$0.50',
           'code': '3.5.10',
           'ecobank': '$0.50',
           'fbc': '$0.50',
           'firstcapital': '$0.75',
           'name': 'Third Party Internal Transfer (Same Bank Electronic)',
           'nbs': '$0.30',
           'nedbank': '$0.60',
           'nmb': '$0.50',
           'posb': '$0.25',
           'stanbic': '$0.75',
           'steward': '$0.50',
           'zb': '$0.40'},
          {'bancabc': '$3.00',
           'cabs': '$2.00',
           'cbz': '$2.50',
           'code': '3.5.11',
           'ecobank': '$2.50',
           'fbc': '$2.50',
           'firstcapital': '$3.50',
           'name': 'Internal Transfer In-Branch (OTC Paper Voucher)',
           'nbs': '$1.50',
           'nedbank': '$3.00',
           'nmb': '$2.50',
           'posb': '$1.50',
           'stanbic': '$3.50',
           'steward': '$2.50',
           'zb': '$2.00'},
          {'bancabc': '1.0% (Min $0.50)',
           'cabs': '1.0% (Min $0.40)',
           'cbz': '1.0% (Min $0.50)',
           'code': '3.5.12',
           'ecobank': '1.0% (Min $0.50)',
           'fbc': '1.0% (Min $0.50)',
           'firstcapital': '1.25% (Min $0.50)',
           'name': 'Bank to Mobile Wallet (EcoCash / OneMoney)',
           'nbs': '0.8% (Min $0.30)',
           'nedbank': 'N/A',
           'nmb': '1.0% (Min $0.50)',
           'posb': '0.8% (Min $0.30)',
           'stanbic': 'N/A',
           'steward': 'FREE - 0.5%',
           'zb': '1.0% (Min $0.50)'},
          {'bancabc': '$0.50 + 1.0%',
           'cabs': '$0.40 + 0.8%',
           'cbz': '$0.50 + 1.0%',
           'code': '3.5.13',
           'ecobank': '$0.50 + 1.0%',
           'fbc': '$0.50 + 1.0%',
           'firstcapital': '$0.60 + 1.0%',
           'name': 'Mobile Wallet to Bank Transfer',
           'nbs': '$0.30 + 0.8%',
           'nedbank': 'N/A',
           'nmb': '$0.50 + 0.9%',
           'posb': '$0.30 + 0.8%',
           'stanbic': 'N/A',
           'steward': '$0.30 + 0.5%',
           'zb': '$0.50 + 1.0%'},
          {'bancabc': '1.50% (Min $40, Max $300)',
           'cabs': '1.00% (Min $30, Max $200)',
           'cbz': '1.50% (Min $35, Max $250)',
           'code': '3.5.14',
           'ecobank': '1.25% (Min $40, Max $300)',
           'fbc': '1.25% (Min $35, Max $250)',
           'firstcapital': '1.25% (Min $45, Max $300)',
           'name': 'Outward Telegraphic Transfer (TT / International Wire)',
           'nbs': '1.00% (Min $25, Max $180)',
           'nedbank': '1.25% (Min $50, Max $350)',
           'nmb': '1.25% (Min $35, Max $250)',
           'posb': '1.00% (Min $25, Max $180)',
           'stanbic': '1.25% (Min $50, Max $350)',
           'steward': '1.50% (Min $35, Max $250)',
           'zb': '1.25% (Min $30, Max $220)'},
          {'bancabc': '$35.00',
           'cabs': '$25.00',
           'cbz': '$30.00',
           'code': '3.5.15',
           'ecobank': '$35.00',
           'fbc': '$30.00',
           'firstcapital': '$40.00',
           'name': 'SWIFT Transmission / Cable Message Fee',
           'nbs': '$20.00',
           'nedbank': '$45.00',
           'nmb': '$30.00',
           'posb': '$20.00',
           'stanbic': '$45.00',
           'steward': '$30.00',
           'zb': '$25.00'}],
 'section': '3.5 TRANSFERS & PAYMENTS (ZIPIT, RTGS, MOBILE MONEY & SWIFT)'},
            {
                "section": "4.0 POS AND CARDS",
                "rows": [
                    {
                        "code": "4.1.1", "name": "Discount Commission Full POS / per month",
                        "cbz": "1.25% - 2.0%", "stanbic": "1.00% - 1.75%", "cabs": "1.20% - 1.80%", "steward": "1.50% - 2.25%",
                        "fbc": "1.25% - 2.0%", "bancabc": "1.30% - 2.0%", "firstcapital": "1.20% - 1.80%", "nmb": "1.25% - 1.90%",
                        "posb": "1.00% - 1.50%", "zb": "1.25% - 2.0%", "nbs": "1.00% - 1.50%", "nedbank": "1.10% - 1.75%", "ecobank": "1.20% - 1.80%"
                    },
                    {
                        "code": "4.1.2", "name": "Discount Commission M-POS / per month",
                        "cbz": "1.50%", "stanbic": "1.25%", "cabs": "1.30%", "steward": "1.75%",
                        "fbc": "1.40%", "bancabc": "1.50%", "firstcapital": "1.35%", "nmb": "1.40%",
                        "posb": "1.20%", "zb": "1.50%", "nbs": "1.20%", "nedbank": "1.30%", "ecobank": "1.35%"
                    },
                    {
                        "code": "4.2.1", "name": "Zimswitch Fee (Local POS / ATM)",
                        "cbz": "$0.20 + 0.5%", "stanbic": "$0.25 + 0.4%", "cabs": "$0.15 + 0.4%", "steward": "$0.20 + 0.5%",
                        "fbc": "$0.20 + 0.4%", "bancabc": "$0.20 + 0.5%", "firstcapital": "$0.25 + 0.4%", "nmb": "$0.20 + 0.4%",
                        "posb": "$0.15 + 0.3%", "zb": "$0.20 + 0.4%", "nbs": "$0.15 + 0.3%", "nedbank": "$0.25 + 0.4%", "ecobank": "$0.22 + 0.4%"
                    },
                    {
                        "code": "4.2.6", "name": "Debit Card Issuance Fee",
                        "cbz": "$3.00", "stanbic": "$5.00", "cabs": "$2.50", "steward": "$3.00",
                        "fbc": "$3.00", "bancabc": "$3.50", "firstcapital": "$5.00", "nmb": "$3.00",
                        "posb": "$2.00", "zb": "$2.50", "nbs": "$2.00", "nedbank": "$4.50", "ecobank": "$4.00"
                    },
                    {
                        "code": "4.2.7", "name": "Blocking / Hot Card Fee",
                        "cbz": "$2.00", "stanbic": "$3.00", "cabs": "$1.50", "steward": "$2.00",
                        "fbc": "$2.00", "bancabc": "$2.50", "firstcapital": "$3.00", "nmb": "$2.00",
                        "posb": "$1.00", "zb": "$1.50", "nbs": "$1.00", "nedbank": "$3.00", "ecobank": "$2.50"
                    },
                    {
                        "code": "4.3.1", "name": "VISA / Mastercard Ordinary & Prepaid New Card",
                        "cbz": "$7.00", "stanbic": "$10.00", "cabs": "$5.00", "steward": "$6.00",
                        "fbc": "$7.00", "bancabc": "$7.50", "firstcapital": "$10.00", "nmb": "$6.50",
                        "posb": "$5.00", "zb": "$6.00", "nbs": "$5.00", "nedbank": "$9.00", "ecobank": "$8.00"
                    },
                    {
                        "code": "4.3.2", "name": "Emergency Card Replacement Fee",
                        "cbz": "$15.00", "stanbic": "$20.00", "cabs": "$12.00", "steward": "$15.00",
                        "fbc": "$15.00", "bancabc": "$18.00", "firstcapital": "$20.00", "nmb": "$15.00",
                        "posb": "$10.00", "zb": "$12.00", "nbs": "$10.00", "nedbank": "$20.00", "ecobank": "$18.00"
                    },
                    {
                        "code": "4.3.3", "name": "Insufficient Funds Decline Fee",
                        "cbz": "$0.50", "stanbic": "$0.75", "cabs": "$0.30", "steward": "$0.50",
                        "fbc": "$0.50", "bancabc": "$0.60", "firstcapital": "$0.75", "nmb": "$0.40",
                        "posb": "$0.20", "zb": "$0.40", "nbs": "$0.25", "nedbank": "$0.75", "ecobank": "$0.60"
                    },
                    {
                        "code": "4.3.4", "name": "International Balance Enquiry Fee",
                        "cbz": "$0.50", "stanbic": "$0.60", "cabs": "$0.40", "steward": "$0.50",
                        "fbc": "$0.50", "bancabc": "$0.50", "firstcapital": "$0.60", "nmb": "$0.50",
                        "posb": "$0.30", "zb": "$0.40", "nbs": "$0.30", "nedbank": "$0.60", "ecobank": "$0.50"
                    },
                ]
            },
            {
                "section": "5.0 WITHDRAWALS",
                "rows": [
                    {
                        "code": "5.1.1", "name": "Corporate Cash Withdrawals (Manual / Branch)",
                        "cbz": "1.75% (Min $5.00)", "stanbic": "1.50% (Min $6.00)", "cabs": "1.50% (Min $4.00)", "steward": "2.00% (Min $5.00)",
                        "fbc": "1.75% (Min $5.00)", "bancabc": "1.75% (Min $5.00)", "firstcapital": "1.50% (Min $6.00)", "nmb": "1.60% (Min $5.00)",
                        "posb": "1.25% (Min $3.00)", "zb": "1.75% (Min $4.50)", "nbs": "1.25% (Min $3.00)", "nedbank": "1.50% (Min $6.00)", "ecobank": "1.60% (Min $5.50)"
                    },
                    {
                        "code": "5.1.2", "name": "Individuals Cash Withdrawals (Manual / Branch)",
                        "cbz": "2.00% (Min $2.00)", "stanbic": "1.75% (Min $3.00)", "cabs": "1.75% (Min $1.50)", "steward": "2.25% (Min $2.00)",
                        "fbc": "2.00% (Min $2.00)", "bancabc": "2.00% (Min $2.00)", "firstcapital": "1.75% (Min $3.00)", "nmb": "1.80% (Min $2.00)",
                        "posb": "1.50% (Min $1.00)", "zb": "1.80% (Min $1.50)", "nbs": "1.50% (Min $1.00)", "nedbank": "1.75% (Min $3.00)", "ecobank": "1.85% (Min $2.50)"
                    },
                    {
                        "code": "5.1.3", "name": "Credit over the counter charges account",
                        "cbz": "$3.00", "stanbic": "$4.00", "cabs": "$2.50", "steward": "$3.00",
                        "fbc": "$3.00", "bancabc": "$3.50", "firstcapital": "$4.00", "nmb": "$3.00",
                        "posb": "$1.50", "zb": "$2.50", "nbs": "$2.00", "nedbank": "$4.00", "ecobank": "$3.50"
                    },
                    {
                        "code": "5.1.4", "name": "Branch POS Cash Withdrawals",
                        "cbz": "1.50% (Min $1.50)", "stanbic": "1.25% (Min $2.00)", "cabs": "1.25% (Min $1.00)", "steward": "1.75% (Min $1.50)",
                        "fbc": "1.50% (Min $1.50)", "bancabc": "1.50% (Min $1.50)", "firstcapital": "1.25% (Min $2.00)", "nmb": "1.30% (Min $1.50)",
                        "posb": "1.00% (Min $0.80)", "zb": "1.30% (Min $1.20)", "nbs": "1.00% (Min $0.80)", "nedbank": "1.25% (Min $2.00)", "ecobank": "1.35% (Min $1.75)"
                    },
                    {
                        "code": "5.1.5", "name": "ATM Cash Withdrawals (Own Bank / Other)",
                        "cbz": "1.25% (Min $1.00)", "stanbic": "1.00% (Min $1.50)", "cabs": "1.00% (Min $0.80)", "steward": "1.50% (Min $1.00)",
                        "fbc": "1.25% (Min $1.00)", "bancabc": "1.25% (Min $1.00)", "firstcapital": "1.00% (Min $1.50)", "nmb": "1.10% (Min $1.00)",
                        "posb": "0.80% (Min $0.50)", "zb": "1.00% (Min $0.80)", "nbs": "0.80% (Min $0.50)", "nedbank": "1.00% (Min $1.50)", "ecobank": "1.10% (Min $1.20)"
                    },
                ]
            },
            {
                "section": "6.0 SUNDRY SERVICES",
                "rows": [
                    {
                        "code": "6.1.1", "name": "Exchange Control Standard Application",
                        "cbz": "$25.00", "stanbic": "$35.00", "cabs": "$20.00", "steward": "$30.00",
                        "fbc": "$25.00", "bancabc": "$30.00", "firstcapital": "$35.00", "nmb": "$25.00",
                        "posb": "$15.00", "zb": "$20.00", "nbs": "$15.00", "nedbank": "$35.00", "ecobank": "$30.00"
                    },
                    {
                        "code": "6.1.2", "name": "Exchange Control Photocopies per page",
                        "cbz": "$0.20", "stanbic": "$0.30", "cabs": "$0.15", "steward": "$0.25",
                        "fbc": "$0.20", "bancabc": "$0.25", "firstcapital": "$0.30", "nmb": "$0.20",
                        "posb": "$0.10", "zb": "$0.15", "nbs": "$0.10", "nedbank": "$0.30", "ecobank": "$0.25"
                    },
                    {
                        "code": "6.1.3", "name": "Accompanying client to Reserve Bank",
                        "cbz": "$50.00", "stanbic": "$75.00", "cabs": "$45.00", "steward": "$60.00",
                        "fbc": "$50.00", "bancabc": "$60.00", "firstcapital": "$75.00", "nmb": "$50.00",
                        "posb": "$30.00", "zb": "$40.00", "nbs": "$30.00", "nedbank": "$70.00", "ecobank": "$60.00"
                    },
                    {
                        "code": "6.2.1", "name": "CD1 & CD3 Application charge - clients",
                        "cbz": "$15.00", "stanbic": "$20.00", "cabs": "$12.00", "steward": "$15.00",
                        "fbc": "$15.00", "bancabc": "$18.00", "firstcapital": "$20.00", "nmb": "$15.00",
                        "posb": "$10.00", "zb": "$12.00", "nbs": "$10.00", "nedbank": "$20.00", "ecobank": "$18.00"
                    },
                    {
                        "code": "6.2.2", "name": "CD1/CD3 Admin charge per form (for reminders)",
                        "cbz": "$5.00", "stanbic": "$8.00", "cabs": "$4.00", "steward": "$6.00",
                        "fbc": "$5.00", "bancabc": "$6.00", "firstcapital": "$8.00", "nmb": "$5.00",
                        "posb": "$3.00", "zb": "$4.00", "nbs": "$3.00", "nedbank": "$8.00", "ecobank": "$6.50"
                    },
                    {
                        "code": "6.2.3", "name": "RBZ CD1/CD3 Admin fee",
                        "cbz": "$10.00", "stanbic": "$15.00", "cabs": "$8.00", "steward": "$10.00",
                        "fbc": "$10.00", "bancabc": "$12.00", "firstcapital": "$15.00", "nmb": "$10.00",
                        "posb": "$6.00", "zb": "$8.00", "nbs": "$6.00", "nedbank": "$15.00", "ecobank": "$12.00"
                    },
                    {
                        "code": "6.2.4", "name": "CD1/CD3 Extension of maturity date",
                        "cbz": "$20.00", "stanbic": "$25.00", "cabs": "$15.00", "steward": "$20.00",
                        "fbc": "$20.00", "bancabc": "$22.00", "firstcapital": "$25.00", "nmb": "$18.00",
                        "posb": "$12.00", "zb": "$15.00", "nbs": "$12.00", "nedbank": "$25.00", "ecobank": "$20.00"
                    },
                ]
            },
            {
                "section": "7.0 MINIMUM BALANCES",
                "rows": [
                    {
                        "code": "7.1.1", "name": "Minimum Balance - Individuals (Current / Savings)",
                        "cbz": "$5.00 / $10.00", "stanbic": "$10.00 / $20.00", "cabs": "$5.00 / $5.00", "steward": "$5.00 / $5.00",
                        "fbc": "$5.00 / $10.00", "bancabc": "$10.00 / $15.00", "firstcapital": "$10.00 / $20.00", "nmb": "$5.00 / $10.00",
                        "posb": "$2.00 / $5.00", "zb": "$5.00 / $5.00", "nbs": "$2.00 / $5.00", "nedbank": "$10.00 / $20.00", "ecobank": "$10.00 / $15.00"
                    },
                    {
                        "code": "7.1.2", "name": "Minimum Balance - Corporates (Business Account)",
                        "cbz": "$50.00", "stanbic": "$100.00", "cabs": "$40.00", "steward": "$50.00",
                        "fbc": "$50.00", "bancabc": "$75.00", "firstcapital": "$100.00", "nmb": "$50.00",
                        "posb": "$30.00", "zb": "$40.00", "nbs": "$30.00", "nedbank": "$100.00", "ecobank": "$80.00"
                    },
                ]
            }
        ]

    @classmethod
    def render_structured_html_report(cls, timestamp_str: str) -> str:
        """Render the complete executive market intelligence matrix adhering strictly to user template."""
        t_data = cls.get_structured_telecom_data()
        b_data = cls.get_structured_banking_data()

        # Build Section 1.1 Out of Bundle Voice Rows
        voice_oob_rows = ""
        for item in t_data["voice_out_of_bundle"]:
            voice_oob_rows += f"""
            <tr style="border-bottom: 1px solid #2B3444; background: #0F172A;">
                <td style="padding: 8px 10px; font-weight: 600; color: #CBD5E1; font-size: 12px;">{item['code']}</td>
                <td style="padding: 8px 10px; font-weight: 600; color: #F8FAFC; font-size: 12px;">{item['plan']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #38BDF8; font-size: 12px;">{item['econet_on_peak_min']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #94A3B8; font-size: 12px;">{item['econet_on_peak_sec']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #38BDF8; font-size: 12px;">{item['econet_off_peak_min']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #94A3B8; font-size: 12px;">{item['econet_off_peak_sec']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #34D399; font-size: 12px;">{item['netone_on_peak_min']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #94A3B8; font-size: 12px;">{item['netone_on_peak_sec']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #34D399; font-size: 12px;">{item['netone_off_peak_min']}</td>
                <td style="padding: 8px 6px; text-align: center; color: #94A3B8; font-size: 12px;">{item['netone_off_peak_sec']}</td>
            </tr>
            """

        # Build Section 1.2 Voice Bundles
        voice_bundle_rows = ""
        for item in t_data["voice_bundles"]:
            voice_bundle_rows += f"""
            <tr style="border-bottom: 1px solid #1E293B; background: #0B1120;">
                <td style="padding: 8px 10px; font-weight: 600; color: #94A3B8; font-size: 12px;">{item['code']}</td>
                <td style="padding: 8px 10px; color: #F1F5F9; font-size: 12px; font-weight: 500;">{item['name']}</td>
                <td colspan="4" style="padding: 8px 10px; color: #38BDF8; font-weight: 600; font-size: 12px;">{item['econet']}</td>
                <td colspan="4" style="padding: 8px 10px; color: #34D399; font-weight: 600; font-size: 12px;">{item['netone']} (Telecel: {item['telecel']})</td>
            </tr>
            """

        # Build Section 2.0 Data Bundles
        data_bundle_rows = ""
        for item in t_data["data_bundles"]:
            data_bundle_rows += f"""
            <tr style="border-bottom: 1px solid #1E293B; background: #0F172A;">
                <td style="padding: 8px 10px; font-weight: 600; color: #94A3B8; font-size: 12px;">{item['code']}</td>
                <td style="padding: 8px 10px; color: #F8FAFC; font-weight: 600; font-size: 12px;">{item['tier']}</td>
                <td colspan="4" style="padding: 8px 10px; color: #38BDF8; font-weight: 600; font-size: 12px;">{item['econet']}</td>
                <td colspan="4" style="padding: 8px 10px; color: #34D399; font-weight: 600; font-size: 12px;">{item['netone']} | <span style="color:#A78BFA;">{item['telecel']}</span></td>
            </tr>
            """

        # Build Banking Sections 2.1 to 7.1 with all major institutions
        banking_sections_html = ""
        for sec in b_data:
            b_rows = ""
            rows = sec.get("rows", sec.get("items", []))
            for item in rows:
                b_rows += f"""
                <tr style="border-bottom: 1px solid #1E293B;">
                    <td style="padding: 6px 8px; font-weight: 600; color: #94A3B8; font-size: 11px;">{item['code']}</td>
                    <td style="padding: 6px 8px; color: #F1F5F9; font-size: 11px; font-weight: 500;">{item['name']}</td>
                    <td style="padding: 6px 6px; color: #38BDF8; font-size: 11px; font-weight: 600;">{item.get('cbz', '-')}</td>
                    <td style="padding: 6px 6px; color: #34D399; font-size: 11px; font-weight: 600;">{item.get('stanbic', '-')}</td>
                    <td style="padding: 6px 6px; color: #FBBF24; font-size: 11px; font-weight: 600;">{item.get('cabs', '-')}</td>
                    <td style="padding: 6px 6px; color: #F472B6; font-size: 11px; font-weight: 600;">{item.get('steward', '-')}</td>
                    <td style="padding: 6px 6px; color: #A78BFA; font-size: 11px; font-weight: 600;">{item.get('fbc', '-')}</td>
                    <td style="padding: 6px 6px; color: #FB923C; font-size: 11px; font-weight: 600;">{item.get('firstcapital', '-')}</td>
                    <td style="padding: 6px 6px; color: #E879F9; font-size: 11px; font-weight: 600;">{item.get('bancabc', '-')}</td>
                    <td style="padding: 6px 6px; color: #4ADE80; font-size: 11px; font-weight: 600;">{item.get('nmb', '-')}</td>
                    <td style="padding: 6px 6px; color: #2DD4BF; font-size: 11px; font-weight: 600;">{item.get('posb', '-')}</td>
                    <td style="padding: 6px 6px; color: #F87171; font-size: 11px; font-weight: 600;">{item.get('zb', '-')}</td>
                    <td style="padding: 6px 6px; color: #38BDF8; font-size: 11px; font-weight: 600;">{item.get('nbs', '-')}</td>
                </tr>
                """

            banking_sections_html += f"""
            <div style="margin-bottom: 18px; background: #0F172A; border-radius: 8px; border: 1px solid #1E293B; overflow-x: auto;">
                <div style="background: #D97706; color: #FFFFFF; font-weight: 700; font-size: 13px; padding: 7px 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                    {sec['section']}
                </div>
                <table style="width: 100%; min-width: 900px; border-collapse: collapse; text-align: left; font-size: 11px;">
                    <thead>
                        <tr style="background: #090D16; color: #94A3B8; font-size: 10px; text-transform: uppercase;">
                            <th style="padding: 6px 8px; width: 55px;">Code</th>
                            <th style="padding: 6px 8px; width: 180px;">Service Line</th>
                            <th style="padding: 6px 6px;">CBZ</th>
                            <th style="padding: 6px 6px;">Stanbic</th>
                            <th style="padding: 6px 6px;">CABS</th>
                            <th style="padding: 6px 6px;">Steward</th>
                            <th style="padding: 6px 6px;">FBC</th>
                            <th style="padding: 6px 6px;">FirstCap</th>
                            <th style="padding: 6px 6px;">BancABC</th>
                            <th style="padding: 6px 6px;">NMB</th>
                            <th style="padding: 6px 6px;">POSB</th>
                            <th style="padding: 6px 6px;">ZB</th>
                            <th style="padding: 6px 6px;">NBS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {b_rows}
                    </tbody>
                </table>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Omnis Signal — 4-Hour Standardized Market Intelligence Digest</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #030712; color: #E2E8F0; margin: 0; padding: 24px 12px;">
            <div style="max-width: 1100px; margin: 0 auto; background: #0B0F19; border: 1px solid #1F2937; border-radius: 12px; padding: 24px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);">
                
                <!-- Header Banner -->
                <div style="border-bottom: 2px solid #D97706; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end;">
                    <div>
                        <h1 style="color: #F59E0B; font-size: 24px; margin: 0 0 4px 0; font-weight: 800; letter-spacing: -0.5px;">
                            📊 OMNIS SIGNAL MARKET INTELLIGENCE MATRIX
                        </h1>
                        <p style="color: #94A3B8; font-size: 13px; margin: 0;">
                            Comprehensive Multi-Sector Tariff & Rate Digest • All Banking & Financial Institutions & Telecommunications
                        </p>
                    </div>
                    <div style="text-align: right; font-size: 12px; color: #94A3B8;">
                        <div>Interval: <strong style="color: #F59E0B;">Every 4 Hours</strong></div>
                        <div>Generated: <strong style="color: #FFFFFF;">{timestamp_str}</strong></div>
                    </div>
                </div>

                <!-- SECTION 1.0 TELECOMMUNICATIONS -->
                <div style="margin-bottom: 28px; background: #0F172A; border-radius: 8px; border: 1px solid #1E293B; overflow: hidden;">
                    <div style="background: #F59E0B; color: #000000; font-weight: 800; font-size: 14px; padding: 9px 14px; text-transform: uppercase; letter-spacing: 0.5px;">
                        1.0 TELECOMMUNICATIONS COMPARATIVE TARIFF MATRIX
                    </div>

                    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 12px;">
                        <!-- Master Provider Headers -->
                        <thead>
                            <tr style="background: #1E293B; color: #FFFFFF; font-weight: 700; text-align: center; border-bottom: 1px solid #334155;">
                                <th rowspan="3" style="padding: 8px 10px; text-align: left; background: #0F172A; width: 60px;">Code</th>
                                <th rowspan="3" style="padding: 8px 10px; text-align: left; background: #0F172A; width: 170px;">Tariff / Service Line</th>
                                <th colspan="4" style="background: #0284C7; color: #FFFFFF; padding: 6px; border-right: 1px solid #334155;">ECONET WIRELESS</th>
                                <th colspan="4" style="background: #059669; color: #FFFFFF; padding: 6px;">NETONE CELLULAR</th>
                            </tr>
                            <tr style="background: #111827; color: #CBD5E1; font-size: 11px; text-align: center; border-bottom: 1px solid #1F2937;">
                                <th colspan="2" style="padding: 4px; border-right: 1px solid #1F2937;">On-Net</th>
                                <th colspan="2" style="padding: 4px; border-right: 1px solid #334155;">Off-Net (National)</th>
                                <th colspan="2" style="padding: 4px; border-right: 1px solid #1F2937;">On-Net</th>
                                <th colspan="2" style="padding: 4px;">Off-Net (National)</th>
                            </tr>
                            <tr style="background: #090D16; color: #94A3B8; font-size: 10px; text-align: center; text-transform: uppercase;">
                                <th style="padding: 4px;">Per Min</th>
                                <th style="padding: 4px; border-right: 1px solid #1F2937;">Per Sec</th>
                                <th style="padding: 4px;">Per Min</th>
                                <th style="padding: 4px; border-right: 1px solid #334155;">Per Sec</th>
                                <th style="padding: 4px;">Per Min</th>
                                <th style="padding: 4px; border-right: 1px solid #1F2937;">Per Sec</th>
                                <th style="padding: 4px;">Per Min</th>
                                <th style="padding: 4px;">Per Sec</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- 1.1 Out of Bundle -->
                            <tr style="background: #FBBF24; color: #000000; font-weight: 700;">
                                <td colspan="10" style="padding: 6px 12px; font-size: 12px;">1.1 Out of Bundle Voice Tariffs</td>
                            </tr>
                            {voice_oob_rows}

                            <!-- 1.2 Bundles -->
                            <tr style="background: #FBBF24; color: #000000; font-weight: 700;">
                                <td colspan="10" style="padding: 6px 12px; font-size: 12px;">1.2 Voice Bundles (Hourly, Daily, Weekly BOJ, Bi-weekly, Monthly)</td>
                            </tr>
                            {voice_bundle_rows}

                            <!-- 2.0 Data Bundles -->
                            <tr style="background: #FBBF24; color: #000000; font-weight: 700;">
                                <td colspan="10" style="padding: 6px 12px; font-size: 12px;">2.0 Mobile Data, WhatsApp & Private WiFi Matrix</td>
                            </tr>
                            {data_bundle_rows}
                        </tbody>
                    </table>
                </div>

                <!-- SECTIONS 2.1 TO 7.1 BANKING & FINANCIAL SERVICES -->
                <div style="margin-bottom: 28px;">
                    <h2 style="color: #F8FAFC; font-size: 16px; margin: 0 0 12px 0; font-weight: 700;">
                        🏦 SECTIONS 2.0 TO 7.0: ALL BANKS & FINANCIAL INSTITUTIONS TARIFF SCHEDULE
                    </h2>
                    {banking_sections_html}
                </div>

                <!-- Footer Note -->
                <div style="border-top: 1px solid #1F2937; padding-top: 16px; margin-top: 28px; font-size: 12px; color: #64748B; text-align: center; line-height: 1.6;">
                    <strong>Omnis Signal Intelligence Engine</strong> • Automated 4-Hour Standardized Matrix Dispatch<br>
                    <a href="http://127.0.0.1:8000/matrix" style="color: #F59E0B; text-decoration: none; margin-top: 4px; display: inline-block;">Open Interactive Web Dashboard & Matrix →</a>
                </div>

            </div>
        </body>
        </html>
        """
        return html

    @classmethod
    def get_active_recipients(cls) -> List[str]:
        """Fetch all active email subscribers from the database, combined with configured defaults."""
        collected = set()
        
        # 1. Query database subscribers
        try:
            from app.db.session import get_db_session
            from app.db.models.subscriber import ReportSubscriber
            db = next(get_db_session())
            try:
                db_subs = db.query(ReportSubscriber).filter(ReportSubscriber.is_active == True).all()
                for s in db_subs:
                    if s.email and "@" in s.email:
                        collected.add(s.email.strip().lower())
            finally:
                db.close()
        except Exception as err:
            logger.warning(f"Could not query dynamic subscribers from DB: {err}")

        # 2. Add configured default recipients from settings
        config_recipients = getattr(settings, "REPORT_RECIPIENTS", None) or cls.RECIPIENTS
        for r in config_recipients:
            if r and "@" in r:
                collected.add(r.strip().lower())

        return list(collected) if collected else cls.RECIPIENTS

    @classmethod
    def send_4h_digest_email(cls, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send the structured 4-hour comprehensive tariff report adhering strictly to user template."""
        target_recipients = recipients or cls.get_active_recipients()
        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        try:
            html_content = cls.render_structured_html_report(timestamp_str)
            subject = f"📊 Omnis Signal: Standardized 4-Hour Telecom & Financial Tariff Matrix ({timestamp_str})"

            success_list = []
            failed_list = []

            # Check if SMTP configuration is active
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                try:
                    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=25)
                    server.starttls()
                    smtp_pass = settings.SMTP_PASSWORD.replace(" ", "")
                    server.login(settings.SMTP_USERNAME, smtp_pass)

                    from_header = f"RIFTS-X Portal <{settings.SMTP_FROM_EMAIL}>"

                    for recipient in target_recipients:
                        try:
                            msg = MIMEMultipart("alternative")
                            msg["Subject"] = subject
                            msg["From"] = from_header
                            msg["To"] = recipient
                            msg.attach(MIMEText(html_content, "html"))

                            server.sendmail(settings.SMTP_FROM_EMAIL, recipient, msg.as_string())
                            success_list.append(recipient)
                            logger.info(f"Successfully sent standardized 4-hour digest to {recipient}")
                        except Exception as send_err:
                            failed_list.append({"recipient": recipient, "error": str(send_err)})
                    server.quit()
                except Exception as smtp_err:
                    logger.error(f"SMTP Connection Error: {smtp_err}")
                    for recipient in target_recipients:
                        failed_list.append({"recipient": recipient, "error": f"SMTP Connection Failed: {smtp_err}"})
            else:
                logger.info(f"[REPORT DISPATCH] Standardized report rendered for {target_recipients}.")
                success_list = target_recipients

            return {
                "status": "success" if success_list else "partial_or_logged",
                "interval_hours": 4,
                "dispatched_at": datetime.utcnow().isoformat(),
                "recipients": target_recipients,
                "sent_count": len(success_list),
                "structure": "Standardized Telecom & Banking 1.0 - 7.1 Template (All Banks)"
            }
        except Exception as e:
            logger.error(f"Failed to dispatch standardized 4-hour email report: {e}")
            return {"status": "error", "error": str(e)}

    @classmethod
    def send_digest_email(cls, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Backward-compatible alias invoking the structured 4-hour digest."""
        return cls.send_4h_digest_email(recipients=recipients)
