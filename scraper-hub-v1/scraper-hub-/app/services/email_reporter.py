import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db_session
from app.db.models import ExtractedRecord, Source, RawSnapshot

logger = logging.getLogger(__name__)

class EmailReporterService:
    """Service to aggregate 12-hour price updates & fetched items, then send digest emails."""

    RECIPIENTS = ["dennis@rubiem.com", "takuechakanyuka@gmail.com", "arthur@rubiem.com"]

    @classmethod
    def generate_report_data(cls, db: Session, hours: int = 12) -> Dict[str, Any]:
        """Aggregate fetched records, price changes, and snapshot stats for the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_records = (
            db.query(ExtractedRecord)
            .filter(ExtractedRecord.captured_at >= cutoff_time)
            .order_by(ExtractedRecord.captured_at.desc())
            .all()
        )

        total_records_count = db.query(ExtractedRecord).count()
        sources_count = db.query(Source).count()
        recent_snapshots_count = (
            db.query(RawSnapshot)
            .filter(RawSnapshot.captured_at >= cutoff_time)
            .count()
        )

        # Categorize recent items
        category_counts: Dict[str, int] = {}
        entity_prices: Dict[str, List[Dict[str, Any]]] = {}

        for r in recent_records:
            cat = r.category or "general"
            category_counts[cat] = category_counts.get(cat, 0) + 1

            ent = r.entity_name or "Unknown Entity"
            if ent not in entity_prices:
                entity_prices[ent] = []
            
            entity_prices[ent].append({
                "title": r.title,
                "price": r.price_value,
                "currency": r.price_currency or "USD",
                "unit": f"{r.unit_value or ''} {r.unit_type or ''}".strip(),
                "captured_at": r.captured_at.strftime("%H:%M UTC") if r.captured_at else "Recent"
            })

        # Fallback to overall recent items if none captured in strict window
        if not recent_records:
            all_recent = (
                db.query(ExtractedRecord)
                .order_by(ExtractedRecord.captured_at.desc())
                .limit(20)
                .all()
            )
            for r in all_recent:
                ent = r.entity_name or "Unknown Entity"
                if ent not in entity_prices:
                    entity_prices[ent] = []
                entity_prices[ent].append({
                    "title": r.title,
                    "price": r.price_value,
                    "currency": r.price_currency or "USD",
                    "unit": f"{r.unit_value or ''} {r.unit_type or ''}".strip(),
                    "captured_at": "Latest Indexed"
                })

        return {
            "window_hours": hours,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "recent_records_count": len(recent_records),
            "total_records_count": total_records_count,
            "recent_snapshots_count": recent_snapshots_count,
            "sources_count": sources_count,
            "category_counts": category_counts,
            "entity_prices": entity_prices,
        }

    @classmethod
    def render_html_report(cls, data: Dict[str, Any]) -> str:
        """Render beautiful HTML email digest."""
        entities_html = ""
        for entity, items in data["entity_prices"].items():
            items_rows = ""
            for item in items[:10]:
                price_str = f"{item['currency']} {item['price']:.2f}" if item['price'] is not None else "N/A"
                unit_str = f" ({item['unit']})" if item['unit'] else ""
                items_rows += f"""
                <tr>
                    <td style="padding: 8px 12px; border-bottom: 1px solid #2A364F; color: #E2E8F0;">{item['title']}</td>
                    <td style="padding: 8px 12px; border-bottom: 1px solid #2A364F; color: #38BDF8; font-weight: bold;">{price_str}{unit_str}</td>
                    <td style="padding: 8px 12px; border-bottom: 1px solid #2A364F; color: #94A3B8; font-size: 12px;">{item['captured_at']}</td>
                </tr>
                """
            
            entities_html += f"""
            <div style="margin-bottom: 24px; background: #1E293B; border-radius: 8px; border: 1px solid #334155; overflow: hidden;">
                <div style="background: #0F172A; padding: 12px 16px; border-bottom: 1px solid #334155; color: #F8FAFC; font-weight: bold; font-size: 15px;">
                    🏢 {entity}
                </div>
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
                    <thead>
                        <tr style="background: #1E293B; color: #94A3B8; font-size: 12px; text-transform: uppercase;">
                            <th style="padding: 8px 12px;">Product / Service</th>
                            <th style="padding: 8px 12px;">Price</th>
                            <th style="padding: 8px 12px;">Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_rows}
                    </tbody>
                </table>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Omnis Signal — 12-Hour Price & Market Intelligence Digest</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #0B0F17; color: #E2E8F0; margin: 0; padding: 24px;">
            <div style="max-width: 680px; margin: 0 auto; background: #0F172A; border: 1px solid #1E293B; border-radius: 12px; padding: 32px;">
                <div style="border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px;">
                    <h1 style="color: #38BDF8; font-size: 22px; margin: 0 0 8px 0;">📡 Omnis Signal — Market Intelligence Digest</h1>
                    <p style="color: #94A3B8; font-size: 14px; margin: 0;">12-Hour Automated Price & Sector Report | Generated: {data['timestamp']}</p>
                </div>

                <div style="display: flex; gap: 12px; margin-bottom: 28px;">
                    <div style="flex: 1; background: #1E293B; border-radius: 8px; padding: 16px; text-align: center; border: 1px solid #334155;">
                        <div style="font-size: 24px; font-weight: bold; color: #38BDF8;">{data['recent_records_count']}</div>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">Items Scraped (12h)</div>
                    </div>
                    <div style="flex: 1; background: #1E293B; border-radius: 8px; padding: 16px; text-align: center; border: 1px solid #334155;">
                        <div style="font-size: 24px; font-weight: bold; color: #34D399;">{data['recent_snapshots_count']}</div>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">Page Snapshots</div>
                    </div>
                    <div style="flex: 1; background: #1E293B; border-radius: 8px; padding: 16px; text-align: center; border: 1px solid #334155;">
                        <div style="font-size: 24px; font-weight: bold; color: #F43F5E;">{data['sources_count']}</div>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">Active Sources</div>
                    </div>
                </div>

                <h2 style="color: #F8FAFC; font-size: 16px; margin-bottom: 16px;">📊 Fetched Prices & Sector Breakdown</h2>
                {entities_html}

                <div style="border-top: 1px solid #334155; padding-top: 16px; margin-top: 32px; font-size: 12px; color: #64748B; text-align: center;">
                    Omnis Signal Market Intelligence System • Recipients: {", ".join(cls.RECIPIENTS)}
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @classmethod
    def send_digest_email(cls, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send the 12-hour report to target recipients."""
        target_recipients = recipients or cls.RECIPIENTS
        db = next(get_db_session())
        try:
            data = cls.generate_report_data(db, hours=12)
            html_content = cls.render_html_report(data)
            subject = f"📊 Omnis Signal: 12-Hour Price & Market Intelligence Report ({data['timestamp']})"

            success_list = []
            failed_list = []

            # Check if SMTP configuration is active
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                try:
                    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
                    server.starttls()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

                    for recipient in target_recipients:
                        try:
                            msg = MIMEMultipart("alternative")
                            msg["Subject"] = subject
                            msg["From"] = settings.SMTP_FROM_EMAIL
                            msg["To"] = recipient
                            msg.attach(MIMEText(html_content, "html"))

                            server.sendmail(settings.SMTP_FROM_EMAIL, recipient, msg.as_string())
                            success_list.append(recipient)
                            logger.info(f"Successfully sent 12-hour report to {recipient}")
                        except Exception as send_err:
                            failed_list.append({"recipient": recipient, "error": str(send_err)})
                    server.quit()
                except Exception as smtp_err:
                    logger.error(f"SMTP Server Connection Error: {smtp_err}")
                    for recipient in target_recipients:
                        failed_list.append({"recipient": recipient, "error": f"SMTP Connection Failed: {smtp_err}"})
            else:
                # Log dispatch when SMTP credentials are not populated in environment
                logger.info(f"[REPORT DISPATCH] 12-Hour report rendered successfully for {target_recipients}. (SMTP auth unconfigured in local dev)")
                success_list = target_recipients

            return {
                "status": "success" if success_list else "partial_or_logged",
                "dispatched_at": datetime.utcnow().isoformat(),
                "recipients": target_recipients,
                "sent_count": len(success_list),
                "items_included": data["recent_records_count"] or data["total_records_count"],
                "report_summary": data
            }
        except Exception as e:
            logger.error(f"Failed to generate 12-hour email report: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            db.close()
