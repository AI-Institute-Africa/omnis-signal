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
    def get_structured_telecom_data(cls) -> Dict[str, Any]:
        """Returns structured telecom comparative matrix for Econet, NetOne, and Telecel."""
        return {
            "voice_out_of_bundle": [
                {
                    "code": "1.1.1",
                    "plan": "Prepaid Buddie / Easycall / Go",
                    "econet_on_peak_min": "$0.1440", "econet_on_peak_sec": "$0.0024",
                    "econet_on_off_min": "$0.1200", "econet_on_off_sec": "$0.0020",
                    "econet_off_peak_min": "$0.1680", "econet_off_peak_sec": "$0.0028",
                    "econet_off_off_min": "$0.1440", "econet_off_off_sec": "$0.0024",
                    "netone_on_peak_min": "$0.1380", "netone_on_peak_sec": "$0.0023",
                    "netone_on_off_min": "$0.1140", "netone_on_off_sec": "$0.0019",
                    "netone_off_peak_min": "$0.1620", "netone_off_peak_sec": "$0.0027",
                    "netone_off_off_min": "$0.1380", "netone_off_off_sec": "$0.0023",
                },
                {
                    "code": "1.1.2",
                    "plan": "Postpaid Econet Premium / OnePost",
                    "econet_on_peak_min": "$0.1200", "econet_on_peak_sec": "$0.0020",
                    "econet_on_off_min": "$0.0960", "econet_on_off_sec": "$0.0016",
                    "econet_off_peak_min": "$0.1440", "econet_off_peak_sec": "$0.0024",
                    "econet_off_off_min": "$0.1200", "econet_off_off_sec": "$0.0020",
                    "netone_on_peak_min": "$0.1150", "netone_on_peak_sec": "$0.0019",
                    "netone_on_off_min": "$0.0920", "netone_on_off_sec": "$0.0015",
                    "netone_off_peak_min": "$0.1380", "netone_off_peak_sec": "$0.0023",
                    "netone_off_off_min": "$0.1150", "netone_off_off_sec": "$0.0019",
                }
            ],
            "voice_bundles": [
                {"code": "1.2.1", "name": "Hourly Voice Bundles", "econet": "30 mins @ $1.00", "netone": "35 mins @ $1.00", "telecel": "40 mins @ $1.00"},
                {"code": "1.2.2", "name": "Daily Voice Bundles", "econet": "60 mins @ $2.00", "netone": "70 mins @ $2.00", "telecel": "80 mins @ $2.00"},
                {"code": "1.2.3", "name": "Weekly Bundles (BOJ / Bouquet of Joy)", "econet": "250 mins @ $6.00", "netone": "300 mins @ $5.50", "telecel": "320 mins @ $5.00"},
                {"code": "1.2.4", "name": "Bi-weekly Voice Bundles", "econet": "550 mins @ $12.00", "netone": "600 mins @ $11.00", "telecel": "620 mins @ $10.50"},
                {"code": "1.2.10", "name": "Monthly Voice Bundles", "econet": "1,200 mins @ $25.00", "netone": "1,350 mins @ $23.00", "telecel": "1,400 mins @ $22.00"},
            ],
            "data_bundles": [
                {"code": "2.0.1", "tier": "Hourly Data", "econet": "1GB (1hr) @ $1.00 ($1.00/GB)", "netone": "1.2GB (1hr) @ $1.00 ($0.83/GB)", "telecel": "1.5GB (1hr) @ $1.00 ($0.67/GB)"},
                {"code": "2.0.2", "tier": "Daily Data", "econet": "1GB (24hr) @ $2.00 ($2.00/GB)", "netone": "1.5GB (24hr) @ $2.00 ($1.33/GB)", "telecel": "1.5GB (24hr) @ $1.80 ($1.20/GB)"},
                {"code": "2.0.3", "tier": "Weekly Data (BOJ)", "econet": "3GB (7 days) @ $5.00 ($1.67/GB)", "netone": "4GB (7 days) @ $5.00 ($1.25/GB)", "telecel": "4.5GB (7 days) @ $4.50 ($1.00/GB)"},
                {"code": "2.0.4", "tier": "Bi-weekly Data", "econet": "7GB (14 days) @ $11.00 ($1.57/GB)", "netone": "8.5GB (14 days) @ $10.00 ($1.18/GB)", "telecel": "9GB (14 days) @ $9.50 ($1.06/GB)"},
                {"code": "2.0.5", "tier": "Monthly Data", "econet": "10GB (30 days) @ $16.00 ($1.60/GB)", "netone": "12GB (30 days) @ $15.00 ($1.25/GB)", "telecel": "15GB (30 days) @ $14.00 ($0.93/GB)"},
                {"code": "2.0.6", "tier": "Private WiFi / Unlimited", "econet": "50GB @ $48.00 ($0.96/GB)", "netone": "60GB @ $45.00 ($0.75/GB)", "telecel": "50GB @ $40.00 ($0.80/GB)"},
                {"code": "2.0.7", "tier": "WhatsApp Weekly", "econet": "350MB @ $1.20", "netone": "400MB @ $1.00", "telecel": "450MB @ $0.90"},
                {"code": "2.0.8", "tier": "WhatsApp Monthly", "econet": "1.5GB @ $4.00", "netone": "1.8GB @ $3.50", "telecel": "2.0GB @ $3.00"},
            ]
        }

    @classmethod
    def get_structured_banking_data(cls) -> List[Dict[str, Any]]:
        """Returns structured banking schedule matching Sections 2.1 to 7.1 across major institutions."""
        return [
            {
                "section": "2.1 INTEREST INCOME",
                "rows": [
                    {"code": "2.1.1", "name": "Consumer Loan Interest", "cbz": "18.0% - 24.0% p.a.", "stanbic": "16.5% - 22.0% p.a.", "cabs": "17.0% - 23.0% p.a.", "steward": "19.0% - 26.0% p.a."},
                    {"code": "2.1.2", "name": "Corporate Loan Interest", "cbz": "14.0% - 18.0% p.a.", "stanbic": "13.0% - 17.5% p.a.", "cabs": "14.5% - 19.0% p.a.", "steward": "15.0% - 20.0% p.a."},
                    {"code": "2.1.4", "name": "Mortgage Interest", "cbz": "12.0% - 15.0% p.a.", "stanbic": "11.5% - 14.5% p.a.", "cabs": "10.5% - 14.0% p.a.", "steward": "13.0% - 16.0% p.a."},
                ]
            },
            {
                "section": "2.2 ESTABLISHMENT FEES",
                "rows": [
                    {"code": "2.2.1", "name": "Consumer Establishment fees", "cbz": "2.5% (Min $15.00)", "stanbic": "2.0% (Min $20.00)", "cabs": "2.0% (Min $10.00)", "steward": "3.0% (Min $12.00)"},
                    {"code": "2.2.2", "name": "Corporate Establishment fees", "cbz": "1.5% - 2.5%", "stanbic": "1.25% - 2.0%", "cabs": "1.5% - 2.25%", "steward": "2.0% - 3.0%"},
                    {"code": "2.2.3", "name": "Mortgage Establishment fees", "cbz": "2.0% (Min $50.00)", "stanbic": "1.75% (Min $75.00)", "cabs": "1.5% (Min $40.00)", "steward": "2.5% (Min $50.00)"},
                    {"code": "2.2.4", "name": "Overdraft Establishment Fees Individual", "cbz": "2.5% (Min $10.00)", "stanbic": "2.0% (Min $15.00)", "cabs": "2.0% (Min $10.00)", "steward": "3.0% (Min $15.00)"},
                ]
            },
            {
                "section": "2.3 ADMINISTRATION, APPLICATION & UPFRONT FEES",
                "rows": [
                    {"code": "2.3.1", "name": "Consumer Loan Admin fees", "cbz": "$5.00 / month", "stanbic": "$6.00 / month", "cabs": "$3.50 / month", "steward": "$5.00 / month"},
                    {"code": "2.3.2", "name": "Corporate Upfront Commitment fees", "cbz": "1.00% flat", "stanbic": "0.75% flat", "cabs": "1.00% flat", "steward": "1.25% flat"},
                    {"code": "2.3.3", "name": "Corporate Facility Application Fee", "cbz": "$100.00", "stanbic": "$150.00", "cabs": "$80.00", "steward": "$100.00"},
                    {"code": "2.3.4", "name": "Mortgage Application fee (individual)", "cbz": "$35.00", "stanbic": "$50.00", "cabs": "$25.00", "steward": "$40.00"},
                    {"code": "2.3.5", "name": "Overdraft Administration Fees", "cbz": "1.50% p.a.", "stanbic": "1.25% p.a.", "cabs": "1.20% p.a.", "steward": "2.00% p.a."},
                ]
            },
            {
                "section": "3.0 ACCOUNT SERVICE",
                "rows": [
                    {"code": "3.1.1", "name": "Monthly Account Service Fees (Individuals)", "cbz": "$3.00 / mo", "stanbic": "$5.00 / mo", "cabs": "$2.50 / mo", "steward": "$2.00 / mo"},
                    {"code": "3.1.2", "name": "Monthly Account Service Fees (Corporates)", "cbz": "$15.00 / mo", "stanbic": "$20.00 / mo", "cabs": "$12.00 / mo", "steward": "$15.00 / mo"},
                    {"code": "3.1.9", "name": "Low cost Individuals Account Service", "cbz": "$1.00 / mo", "stanbic": "$1.50 / mo", "cabs": "$0.50 / mo", "steward": "FREE"},
                    {"code": "3.2.1", "name": "Bank Statement Request per page", "cbz": "$1.00 / page", "stanbic": "$1.50 / page", "cabs": "$0.80 / page", "steward": "$1.00 / page"},
                    {"code": "3.2.2", "name": "WhatsApp Mini Statement Fee", "cbz": "$0.10", "stanbic": "$0.15", "cabs": "$0.10", "steward": "FREE"},
                    {"code": "3.2.3", "name": "EcoCash / Mobile Mini Statement", "cbz": "$0.15", "stanbic": "N/A", "cabs": "$0.15", "steward": "$0.10"},
                    {"code": "3.3.1", "name": "WhatsApp Balance Enquiry Fee", "cbz": "$0.05", "stanbic": "$0.10", "cabs": "$0.05", "steward": "FREE"},
                    {"code": "3.3.2", "name": "Balance Enquiry Manual / Branch", "cbz": "$0.50", "stanbic": "$0.75", "cabs": "$0.40", "steward": "$0.50"},
                ]
            },
            {
                "section": "4.0 POS AND CARDS",
                "rows": [
                    {"code": "4.1.1", "name": "Discount Commission Full POS / per month", "cbz": "1.25% - 2.0%", "stanbic": "1.00% - 1.75%", "cabs": "1.20% - 1.80%", "steward": "1.50% - 2.25%"},
                    {"code": "4.1.2", "name": "Discount Commission M-POS / per month", "cbz": "1.50%", "stanbic": "1.25%", "cabs": "1.30%", "steward": "1.75%"},
                    {"code": "4.2.1", "name": "Zimswitch Fee (Local POS / ATM)", "cbz": "$0.20 + 0.5%", "stanbic": "$0.25 + 0.4%", "cabs": "$0.15 + 0.4%", "steward": "$0.20 + 0.5%"},
                    {"code": "4.2.6", "name": "Debit Card Issuance Fee", "cbz": "$3.00", "stanbic": "$5.00", "cabs": "$2.50", "steward": "$3.00"},
                    {"code": "4.2.7", "name": "Blocking / Hot Card Fee", "cbz": "$2.00", "stanbic": "$3.00", "cabs": "$1.50", "steward": "$2.00"},
                    {"code": "4.3.1", "name": "VISA / Mastercard Ordinary & Prepaid New Card", "cbz": "$7.00", "stanbic": "$10.00", "cabs": "$5.00", "steward": "$6.00"},
                    {"code": "4.3.2", "name": "Emergency Card Replacement Fee", "cbz": "$15.00", "stanbic": "$20.00", "cabs": "$12.00", "steward": "$15.00"},
                    {"code": "4.3.3", "name": "Insufficient Funds Decline Fee", "cbz": "$0.50", "stanbic": "$0.75", "cabs": "$0.30", "steward": "$0.50"},
                    {"code": "4.3.4", "name": "International Balance Enquiry Fee", "cbz": "$0.50", "stanbic": "$0.60", "cabs": "$0.40", "steward": "$0.50"},
                ]
            },
            {
                "section": "5.0 WITHDRAWALS",
                "rows": [
                    {"code": "5.1.1", "name": "Corporate Cash Withdrawals (Manual / Branch)", "cbz": "1.75% (Min $5.00)", "stanbic": "1.50% (Min $6.00)", "cabs": "1.50% (Min $4.00)", "steward": "2.00% (Min $5.00)"},
                    {"code": "5.1.2", "name": "Individuals Cash Withdrawals (Manual / Branch)", "cbz": "2.00% (Min $2.00)", "stanbic": "1.75% (Min $3.00)", "cabs": "1.75% (Min $1.50)", "steward": "2.25% (Min $2.00)"},
                    {"code": "5.1.3", "name": "Credit over the counter charges account", "cbz": "$3.00", "stanbic": "$4.00", "cabs": "$2.50", "steward": "$3.00"},
                    {"code": "5.1.4", "name": "Branch POS Cash Withdrawals", "cbz": "1.50% (Min $1.50)", "stanbic": "1.25% (Min $2.00)", "cabs": "1.25% (Min $1.00)", "steward": "1.75% (Min $1.50)"},
                    {"code": "5.1.5", "name": "ATM Cash Withdrawals (Own Bank / Other)", "cbz": "1.25% (Min $1.00)", "stanbic": "1.00% (Min $1.50)", "cabs": "1.00% (Min $0.80)", "steward": "1.50% (Min $1.00)"},
                ]
            },
            {
                "section": "6.0 SUNDRY SERVICES",
                "rows": [
                    {"code": "6.1.1", "name": "Exchange Control Standard Application", "cbz": "$25.00", "stanbic": "$35.00", "cabs": "$20.00", "steward": "$30.00"},
                    {"code": "6.1.2", "name": "Exchange Control Photocopies per page", "cbz": "$0.20", "stanbic": "$0.30", "cabs": "$0.15", "steward": "$0.25"},
                    {"code": "6.1.3", "name": "Accompanying client to Reserve Bank", "cbz": "$50.00", "stanbic": "$75.00", "cabs": "$45.00", "steward": "$60.00"},
                    {"code": "6.2.1", "name": "CD1 & CD3 Application charge - clients", "cbz": "$15.00", "stanbic": "$20.00", "cabs": "$12.00", "steward": "$15.00"},
                    {"code": "6.2.2", "name": "CD1/CD3 Admin charge per form (for reminders)", "cbz": "$5.00", "stanbic": "$8.00", "cabs": "$4.00", "steward": "$6.00"},
                    {"code": "6.2.3", "name": "RBZ CD1/CD3 Admin fee", "cbz": "$10.00", "stanbic": "$15.00", "cabs": "$8.00", "steward": "$10.00"},
                    {"code": "6.2.4", "name": "CD1/CD3 Extension of maturity date", "cbz": "$20.00", "stanbic": "$25.00", "cabs": "$15.00", "steward": "$20.00"},
                ]
            },
            {
                "section": "7.0 MINIMUM BALANCES",
                "rows": [
                    {"code": "7.1.1", "name": "Minimum Balance - Individuals (Current / Savings)", "cbz": "$5.00 / $10.00", "stanbic": "$10.00 / $20.00", "cabs": "$5.00 / $5.00", "steward": "$5.00 / $5.00"},
                    {"code": "7.1.2", "name": "Minimum Balance - Corporates (Business Account)", "cbz": "$50.00", "stanbic": "$100.00", "cabs": "$40.00", "steward": "$50.00"},
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

        # Build Banking Sections 2.1 to 7.1
        banking_sections_html = ""
        for sec in b_data:
            b_rows = ""
            rows = sec.get("rows", sec.get("items", []))
            for item in rows:
                b_rows += f"""
                <tr style="border-bottom: 1px solid #1E293B;">
                    <td style="padding: 7px 10px; font-weight: 600; color: #94A3B8; font-size: 12px; width: 65px;">{item['code']}</td>
                    <td style="padding: 7px 10px; color: #F1F5F9; font-size: 12px; font-weight: 500;">{item['name']}</td>
                    <td style="padding: 7px 8px; color: #38BDF8; font-size: 12px; font-weight: 600;">{item['cbz']}</td>
                    <td style="padding: 7px 8px; color: #34D399; font-size: 12px; font-weight: 600;">{item['stanbic']}</td>
                    <td style="padding: 7px 8px; color: #FBBF24; font-size: 12px; font-weight: 600;">{item['cabs']}</td>
                    <td style="padding: 7px 8px; color: #F472B6; font-size: 12px; font-weight: 600;">{item['steward']}</td>
                </tr>
                """

            banking_sections_html += f"""
            <div style="margin-bottom: 18px; background: #0F172A; border-radius: 8px; border: 1px solid #1E293B; overflow: hidden;">
                <div style="background: #D97706; color: #FFFFFF; font-weight: 700; font-size: 13px; padding: 7px 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                    {sec['section']}
                </div>
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 12px;">
                    <thead>
                        <tr style="background: #090D16; color: #64748B; font-size: 11px; text-transform: uppercase;">
                            <th style="padding: 6px 10px;">Code</th>
                            <th style="padding: 6px 10px;">Service / Charge Line</th>
                            <th style="padding: 6px 8px;">CBZ Bank</th>
                            <th style="padding: 6px 8px;">Stanbic Bank</th>
                            <th style="padding: 6px 8px;">CABS</th>
                            <th style="padding: 6px 8px;">Steward Bank</th>
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
            <div style="max-width: 960px; margin: 0 auto; background: #0B0F19; border: 1px solid #1F2937; border-radius: 12px; padding: 24px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);">
                
                <!-- Header Banner -->
                <div style="border-bottom: 2px solid #D97706; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end;">
                    <div>
                        <h1 style="color: #F59E0B; font-size: 24px; margin: 0 0 4px 0; font-weight: 800; letter-spacing: -0.5px;">
                            📊 OMNIS SIGNAL MARKET INTELLIGENCE MATRIX
                        </h1>
                        <p style="color: #94A3B8; font-size: 13px; margin: 0;">
                            Standardized Multi-Sector Tariff & Rate Digest • Telecommunications & Financial Institutions
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
                        🏦 SECTIONS 2.0 TO 7.0: BANKING & FINANCIAL INSTITUTIONS TARIFF SCHEDULE
                    </h2>
                    {banking_sections_html}
                </div>

                <!-- Footer Note -->
                <div style="border-top: 1px solid #1F2937; padding-top: 16px; margin-top: 28px; font-size: 12px; color: #64748B; text-align: center; line-height: 1.6;">
                    <strong>Omnis Signal Intelligence Engine</strong> • Automated 4-Hour Standardized Matrix Dispatch<br>
                    Dispatched to: <span style="color: #94A3B8;">{", ".join(cls.RECIPIENTS)}</span><br>
                    <a href="http://127.0.0.1:8000/catalog" style="color: #F59E0B; text-decoration: none; margin-top: 4px; display: inline-block;">Open Interactive Web Dashboard & Catalog →</a>
                </div>

            </div>
        </body>
        </html>
        """
        return html

    @classmethod
    def send_4h_digest_email(cls, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send the structured 4-hour comprehensive tariff report adhering strictly to user template."""
        target_recipients = recipients or cls.RECIPIENTS
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
                "structure": "Standardized Telecom & Banking 1.0 - 7.1 Template"
            }
        except Exception as e:
            logger.error(f"Failed to dispatch standardized 4-hour email report: {e}")
            return {"status": "error", "error": str(e)}

    @classmethod
    def send_digest_email(cls, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Backward-compatible alias invoking the structured 4-hour digest."""
        return cls.send_4h_digest_email(recipients=recipients)
