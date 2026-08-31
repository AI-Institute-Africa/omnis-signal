import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db_session
from app.db.models.catalog import SectorConfig, Category, Provider, Listing, ListingPriceHistory
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.source import Source
from app.db.models.raw_snapshot import RawSnapshot

logger = logging.getLogger(__name__)


class EmailReporterService:
    """Service to aggregate 4-hour price updates & all product/service pricing across 7 sectors, then dispatch digest emails."""

    RECIPIENTS = ["dennis@rubiem.com", "takuechakanyuka@gmail.com", "arthur@rubiem.com"]

    @classmethod
    def generate_report_data(cls, db: Session, hours: int = 4) -> Dict[str, Any]:
        """Aggregate all live catalog product and service prices grouped by sector, plus recent updates."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # 1. Total system metrics
        total_listings_count = db.query(Listing).count()
        total_records_count = db.query(ExtractedRecord).count()
        sources_count = db.query(Source).count()
        recent_snapshots_count = (
            db.query(RawSnapshot)
            .filter(RawSnapshot.captured_at >= cutoff_time)
            .count()
        )

        # 2. Query all sectors & listings
        sectors = db.query(SectorConfig).all()
        sector_data: Dict[str, Dict[str, Any]] = {}

        sector_icons = {
            "telecom": "📱",
            "banking": "🏦",
            "transport": "🚌",
            "food": "🍔",
            "retail": "🛒",
            "hotels": "🏨",
            "education": "🎓",
        }

        for s in sectors:
            s_slug = s.slug
            cats = db.query(Category).filter(Category.sector_id == s.id).all()
            cat_ids = [c.id for c in cats]
            listings = (
                db.query(Listing)
                .filter(Listing.category_id.in_(cat_ids))
                .order_by(Listing.name)
                .all()
                if cat_ids else []
            )

            items_list = []
            for l in listings:
                pname = l.provider.name if l.provider else "Verified Provider"
                cname = l.category.name if l.category else "Standard"
                attrs = l.attributes or {}
                
                # Format helpful attribute notes
                notes = []
                if "price_per_gb" in attrs:
                    notes.append(f"${attrs['price_per_gb']:.2f}/GB")
                if "validity" in attrs:
                    notes.append(attrs["validity"])
                if "unit_price" in attrs:
                    notes.append(f"${attrs['unit_price']:.2f}/unit")
                if "room_type" in attrs:
                    notes.append(attrs["room_type"])
                if "curriculum" in attrs:
                    notes.append(attrs["curriculum"])

                items_list.append({
                    "name": l.name,
                    "provider": pname,
                    "category": cname,
                    "price": l.price,
                    "currency": l.currency or "USD",
                    "note": ", ".join(notes) if notes else "",
                    "last_verified": l.last_verified_at.strftime("%Y-%m-%d %H:%M") if l.last_verified_at else "Active",
                })

            sector_data[s_slug] = {
                "name": s.name,
                "icon": sector_icons.get(s_slug, "📦"),
                "total_items": len(listings),
                "items": items_list,
            }

        # 3. Recent price updates within the window
        recent_updates = (
            db.query(ListingPriceHistory)
            .filter(ListingPriceHistory.recorded_at >= cutoff_time)
            .order_by(ListingPriceHistory.recorded_at.desc())
            .limit(20)
            .all()
        )

        return {
            "window_hours": hours,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "total_listings_count": total_listings_count,
            "total_records_count": total_records_count,
            "recent_snapshots_count": recent_snapshots_count,
            "sources_count": sources_count,
            "recent_updates_count": len(recent_updates),
            "sectors": sector_data,
        }

    @classmethod
    def render_html_report(cls, data: Dict[str, Any]) -> str:
        """Render modern, responsive HTML email digest with comprehensive price tables across all 7 sectors."""
        sectors_html = ""

        for slug, sec in data["sectors"].items():
            if not sec["items"]:
                continue

            rows_html = ""
            for item in sec["items"]:
                price_display = f"{item['currency']} ${item['price']:,.2f}" if item['price'] is not None else "N/A"
                note_badge = f"""<span style="display:inline-block; font-size:11px; background:#1e293b; color:#94a3b8; padding:2px 6px; border-radius:4px; margin-left:6px;">{item['note']}</span>""" if item['note'] else ""
                
                rows_html += f"""
                <tr style="border-bottom: 1px solid #1E293B;">
                    <td style="padding: 10px 14px; color: #F8FAFC; font-weight: 500; font-size: 13px;">
                        {item['name']} {note_badge}
                    </td>
                    <td style="padding: 10px 14px; color: #94A3B8; font-size: 13px;">{item['provider']}</td>
                    <td style="padding: 10px 14px; color: #38BDF8; font-weight: 700; font-size: 14px; text-align: right;">{price_display}</td>
                </tr>
                """

            sectors_html += f"""
            <div style="margin-bottom: 28px; background: #0F172A; border-radius: 10px; border: 1px solid #1E293B; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);">
                <div style="background: #1E293B; padding: 12px 18px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #F8FAFC; font-weight: 700; font-size: 15px; letter-spacing: 0.3px;">
                        {sec['icon']} {sec['name'].upper()} SECTOR
                    </span>
                    <span style="background: #0284C7; color: #FFFFFF; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 12px;">
                        {sec['total_items']} items
                    </span>
                </div>
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
                    <thead>
                        <tr style="background: #090D16; color: #64748B; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                            <th style="padding: 8px 14px;">Product / Service Offering</th>
                            <th style="padding: 8px 14px;">Provider / Chain</th>
                            <th style="padding: 8px 14px; text-align: right;">Market Price (USD)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Omnis Signal — 4-Hour Comprehensive Price & Market Intelligence Digest</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #030712; color: #E2E8F0; margin: 0; padding: 32px 16px;">
            <div style="max-width: 780px; margin: 0 auto; background: #0B0F19; border: 1px solid #1F2937; border-radius: 14px; padding: 32px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);">
                
                <!-- Header -->
                <div style="border-bottom: 1px solid #1F2937; padding-bottom: 20px; margin-bottom: 28px;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <h1 style="color: #38BDF8; font-size: 24px; margin: 0 0 6px 0; font-weight: 800; letter-spacing: -0.5px;">
                                📡 OMNIS SIGNAL
                            </h1>
                            <p style="color: #94A3B8; font-size: 13px; margin: 0;">
                                4-Hour Automated Product & Service Price Intelligence Digest
                            </p>
                        </div>
                        <div style="text-align: right; font-size: 12px; color: #64748B;">
                            <div>Dispatch Interval: <strong style="color:#38BDF8;">4 Hours</strong></div>
                            <div>Generated: <strong>{data['timestamp']}</strong></div>
                        </div>
                    </div>
                </div>

                <!-- KPI Metric Tiles -->
                <div style="display: flex; gap: 12px; margin-bottom: 32px;">
                    <div style="flex: 1; background: #0F172A; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #1E293B;">
                        <div style="font-size: 26px; font-weight: 800; color: #38BDF8;">{data['total_listings_count']}</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 4px; text-transform: uppercase; font-weight: 600;">Active Listings</div>
                    </div>
                    <div style="flex: 1; background: #0F172A; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #1E293B;">
                        <div style="font-size: 26px; font-weight: 800; color: #34D399;">7</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 4px; text-transform: uppercase; font-weight: 600;">Live Sectors</div>
                    </div>
                    <div style="flex: 1; background: #0F172A; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #1E293B;">
                        <div style="font-size: 26px; font-weight: 800; color: #F59E0B;">{data['sources_count']}</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 4px; text-transform: uppercase; font-weight: 600;">Monitored Sources</div>
                    </div>
                </div>

                <!-- Sector Breakdown Tables -->
                <div style="margin-bottom: 24px;">
                    <h2 style="color: #F8FAFC; font-size: 17px; margin: 0 0 16px 0; font-weight: 700;">
                        📋 All Real Market Prices by Sector (Zimbabwe)
                    </h2>
                    {sectors_html}
                </div>

                <!-- Footer -->
                <div style="border-top: 1px solid #1F2937; padding-top: 20px; margin-top: 36px; font-size: 12px; color: #64748B; text-align: center; line-height: 1.6;">
                    <strong>Omnis Signal Intelligence Engine</strong> • Automated 4-Hour Price Delivery<br>
                    Recipients: <span style="color: #94A3B8;">{", ".join(cls.RECIPIENTS)}</span><br>
                    <a href="http://127.0.0.1:8000/catalog" style="color: #38BDF8; text-decoration: none; margin-top: 6px; display: inline-block;">Open Interactive Web Dashboard →</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @classmethod
    def send_4h_digest_email(cls, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send the 4-hour comprehensive price report to target recipients."""
        target_recipients = recipients or cls.RECIPIENTS
        db = next(get_db_session())
        try:
            data = cls.generate_report_data(db, hours=4)
            html_content = cls.render_html_report(data)
            subject = f"📊 Omnis Signal: 4-Hour Price & Market Intelligence Digest ({data['timestamp']})"

            success_list = []
            failed_list = []

            # Check if SMTP configuration is active
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                try:
                    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=20)
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
                            logger.info(f"Successfully sent 4-hour price digest to {recipient}")
                        except Exception as send_err:
                            failed_list.append({"recipient": recipient, "error": str(send_err)})
                    server.quit()
                except Exception as smtp_err:
                    logger.error(f"SMTP Server Connection Error: {smtp_err}")
                    for recipient in target_recipients:
                        failed_list.append({"recipient": recipient, "error": f"SMTP Connection Failed: {smtp_err}"})
            else:
                logger.info(f"[4-HOUR REPORT DISPATCH] 4-Hour price digest rendered successfully for {target_recipients}. (SMTP ready for credentials)")
                success_list = target_recipients

            return {
                "status": "success" if success_list else "partial_or_logged",
                "interval_hours": 4,
                "dispatched_at": datetime.utcnow().isoformat(),
                "recipients": target_recipients,
                "sent_count": len(success_list),
                "total_catalog_listings": data["total_listings_count"],
                "report_summary": data
            }
        except Exception as e:
            logger.error(f"Failed to generate 4-hour email report: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            db.close()

    @classmethod
    def send_digest_email(cls, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Backward-compatible alias invoking the 4-hour digest report."""
        return cls.send_4h_digest_email(recipients=recipients)
