import httpx
from datetime import datetime
from app.config import settings
from app.db.models.webhook_target import WebhookTarget
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.webhook_delivery_attempt import WebhookDeliveryAttempt, DeliveryStatus
from app.services.webhook_publisher import WebhookPublisher


def test_publish_record_success(client, db, monkeypatch):
    snapshot = RawSnapshot(url="https://example.org", content="<html></html>", content_type="text/html")
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    target = WebhookTarget(name="Target Success", url="https://example.com/webhook", secret="super-secret-key")
    db.add(target)
    db.commit()
    db.refresh(target)

    record = ExtractedRecord(
        snapshot_id=snapshot.id,
        entity_name="TestEntity",
        category="telecom",
        title="Offer",
        source_url="https://example.org/page",
        captured_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    def fake_post(url, json, headers, timeout):
        return httpx.Response(200, request=httpx.Request("POST", url), content=b"ok")

    monkeypatch.setattr(httpx, "post", fake_post)

    publisher = WebhookPublisher(db)
    publisher.publish_record(record)

    attempt = db.query(WebhookDeliveryAttempt).one()
    assert attempt.status == DeliveryStatus.SUCCESS
    assert attempt.attempt_count == 1
    assert attempt.error_message is None


def test_publish_record_dead_letter_and_replay_success(client, db, monkeypatch):
    snapshot = RawSnapshot(url="https://example.org", content="<html></html>", content_type="text/html")
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    target = WebhookTarget(name="Target Replay", url="https://example.com/webhook", secret="super-secret-key")
    db.add(target)
    db.commit()
    db.refresh(target)

    record = ExtractedRecord(
        snapshot_id=snapshot.id,
        entity_name="TestEntity",
        category="telecom",
        title="Retry Offer",
        source_url="https://example.org/page",
        captured_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    original_max_retries = settings.WEBHOOK_MAX_RETRIES
    settings.WEBHOOK_MAX_RETRIES = 1

    call_count = {"count": 0}

    def fake_post(url, json, headers, timeout):
        call_count["count"] += 1
        return httpx.Response(500, request=httpx.Request("POST", url), content=b"error")

    monkeypatch.setattr(httpx, "post", fake_post)

    try:
        publisher = WebhookPublisher(db)
        publisher.publish_record(record)

        attempt = db.query(WebhookDeliveryAttempt).one()
        assert attempt.status == DeliveryStatus.DEAD_LETTER
        assert attempt.attempt_count == 1
        assert attempt.error_message is not None

        def success_post(url, json, headers, timeout):
            return httpx.Response(200, request=httpx.Request("POST", url), content=b"ok")

        monkeypatch.setattr(httpx, "post", success_post)
        publisher.replay_failed_deliveries()

        attempt = db.query(WebhookDeliveryAttempt).one()
        assert attempt.status == DeliveryStatus.SUCCESS
        assert attempt.attempt_count == 2
        assert attempt.error_message is None
    finally:
        settings.WEBHOOK_MAX_RETRIES = original_max_retries


def test_replay_failed_deliveries_route(client, db, monkeypatch):
    snapshot = RawSnapshot(url="https://example.org", content="<html></html>", content_type="text/html")
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    target = WebhookTarget(name="Target Route", url="https://example.com/webhook", secret="route-secret-key")
    db.add(target)
    db.commit()
    db.refresh(target)

    record = ExtractedRecord(
        snapshot_id=snapshot.id,
        entity_name="TestEntity",
        category="banking",
        title="Route Offer",
        source_url="https://example.org/page",
        captured_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    attempt = WebhookDeliveryAttempt(
        target_id=target.id,
        record_id=record.id,
        payload="{}",
        status=DeliveryStatus.FAILED,
        attempt_count=1,
    )
    db.add(attempt)
    db.commit()

    def success_post(url, json, headers, timeout):
        return httpx.Response(200, request=httpx.Request("POST", url), content=b"ok")

    monkeypatch.setattr(httpx, "post", success_post)

    response = client.post(f"/api/v1/webhook-targets/{target.id}/replay-failed")
    assert response.status_code == 200
    db.refresh(attempt)
    assert attempt.status == DeliveryStatus.SUCCESS
