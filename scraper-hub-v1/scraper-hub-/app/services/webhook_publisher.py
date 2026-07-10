import json
import hmac
import hashlib
from datetime import datetime
from typing import Tuple

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models.webhook_delivery_attempt import DeliveryStatus, WebhookDeliveryAttempt
from app.db.models.webhook_target import WebhookTarget
from app.db.models.extracted_record import ExtractedRecord
from app.logging import logger


class WebhookPublisher:
    def __init__(self, db: Session):
        self.db = db
        self.max_retries = settings.WEBHOOK_MAX_RETRIES
        self.timeout = settings.WEBHOOK_REQUEST_TIMEOUT

    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC SHA256 signature for the payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _send_webhook(self, url: str, payload: dict, signature: str) -> Tuple[bool, str]:
        """Send webhook request and return (success, error_message)."""
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": f"sha256={signature}",
            "User-Agent": "ScraperHub-Webhook/1.0",
        }

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=self.timeout)
            if 200 <= response.status_code < 300:
                return True, ""
            return False, f"HTTP {response.status_code}: {response.text}"
        except httpx.RequestError as exc:
            return False, f"Request failed: {str(exc)}"

    def publish_record(self, record: ExtractedRecord):
        """Publish an extracted record to all active webhook targets."""
        # Get all active targets
        targets = self.db.query(WebhookTarget).filter(WebhookTarget.is_active.is_(True)).all()

        if not targets:
            logger.info("No active webhook targets found")
            return

        # Prepare payload
        payload = {
            "record_id": record.id,
            "entity_name": record.entity_name,
            "category": record.category,
            "subcategory": record.subcategory,
            "title": record.title,
            "item_name": record.item_name,
            "description": record.description,
            "price_value": record.price_value,
            "price_currency": record.price_currency,
            "billing_period": record.billing_period,
            "unit_value": record.unit_value,
            "unit_type": record.unit_type,
            "eligibility": record.eligibility,
            "effective_date": record.effective_date.isoformat() if record.effective_date else None,
            "captured_at": record.captured_at.isoformat(),
            "source_url": record.source_url,
            "confidence_score": record.confidence_score
        }
        
        payload_str = json.dumps(payload, sort_keys=True)
        
        for target in targets:
            self._publish_to_target(target, record.id, payload, payload_str)

    def _publish_to_target(self, target: WebhookTarget, record_id: int, payload: dict, payload_str: str):
        """Publish to a specific target with retry logic."""
        signature = self._generate_signature(payload_str, target.secret)

        attempt = WebhookDeliveryAttempt(
            target_id=target.id,
            record_id=record_id,
            payload=payload_str,
            status=DeliveryStatus.PENDING,
            attempt_count=0,
        )
        self.db.add(attempt)
        self.db.commit()

        success = False
        error_msg = ""

        for attempt_num in range(1, self.max_retries + 1):
            attempt.attempt_count = attempt_num
            attempt.last_attempt_at = datetime.utcnow()

            success, error_msg = self._send_webhook(target.url, payload, signature)

            if success:
                attempt.status = DeliveryStatus.SUCCESS
                attempt.error_message = None
                logger.info(
                    "Webhook delivered successfully to %s (attempt %s)",
                    target.name,
                    attempt_num,
                )
                break

            attempt.status = DeliveryStatus.FAILED
            attempt.error_message = self._format_error_message(error_msg)
            logger.warning(
                "Webhook delivery failed to %s (attempt %s): %s",
                target.name,
                attempt_num,
                attempt.error_message,
            )

        if not success:
            attempt.status = DeliveryStatus.DEAD_LETTER
            logger.error(
                "Webhook delivery to %s moved to dead letter queue after %s attempts",
                target.name,
                self.max_retries,
            )

        self.db.commit()

    def replay_failed_deliveries(self, target_id: int = None):
        """Replay failed deliveries for a specific target or all targets."""
        query = self.db.query(WebhookDeliveryAttempt).filter(
            WebhookDeliveryAttempt.status.in_([DeliveryStatus.FAILED, DeliveryStatus.DEAD_LETTER])
        )

        if target_id:
            query = query.filter(WebhookDeliveryAttempt.target_id == target_id)

        failed_attempts = query.all()

        for attempt in failed_attempts:
            target = self.db.query(WebhookTarget).filter(WebhookTarget.id == attempt.target_id).first()
            if not target or not target.is_active:
                logger.warning(
                    "Skipping replay for target %s because it is missing or inactive",
                    attempt.target_id,
                )
                continue

            payload = json.loads(attempt.payload)
            signature = self._generate_signature(attempt.payload, target.secret)

            success, error_msg = self._send_webhook(target.url, payload, signature)
            attempt.attempt_count += 1
            attempt.last_attempt_at = datetime.utcnow()

            if success:
                attempt.status = DeliveryStatus.SUCCESS
                attempt.error_message = None
                logger.info(
                    "Replayed webhook delivery successful for target %s, record %s",
                    target.name,
                    attempt.record_id,
                )
            else:
                attempt.error_message = self._format_error_message(error_msg)
                logger.warning(
                    "Replay webhook delivery failed for target %s, record %s: %s",
                    target.name,
                    attempt.record_id,
                    attempt.error_message,
                )
                if attempt.status == DeliveryStatus.FAILED and attempt.attempt_count >= self.max_retries:
                    attempt.status = DeliveryStatus.DEAD_LETTER
                    logger.error(
                        "Webhook delivery to %s remains in dead letter after replay attempts",
                        target.name,
                    )

        self.db.commit()

    def _format_error_message(self, error_message: str) -> str:
        return error_message[:2000] if error_message else ""
