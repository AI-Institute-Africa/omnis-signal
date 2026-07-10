import pytest
from app.db.models.webhook_target import WebhookTarget


def test_create_webhook_target(client, db):
    target_data = {
        "name": "Test Webhook",
        "url": "https://example.com/webhook",
        "secret": "test-secret-key"
    }
    
    response = client.post("/api/v1/webhook-targets/", json=target_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == target_data["name"]
    assert data["url"] == target_data["url"]
    assert data["is_active"] == True
    
    # Verify in database
    db_target = db.query(WebhookTarget).filter(WebhookTarget.id == data["id"]).first()
    assert db_target is not None
    assert db_target.name == target_data["name"]


def test_list_webhook_targets(client, db):
    # Create a target first
    target = WebhookTarget(
        name="Test Target",
        url="https://example.com/webhook",
        secret="secret"
    )
    db.add(target)
    db.commit()
    
    response = client.get("/api/v1/webhook-targets/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Target"


def test_update_webhook_target(client, db):
    # Create a target first
    target = WebhookTarget(
        name="Original Name",
        url="https://example.com/webhook",
        secret="secret"
    )
    db.add(target)
    db.commit()
    
    update_data = {"name": "Updated Name"}
    response = client.patch(f"/api/v1/webhook-targets/{target.id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Updated Name"


def test_delete_webhook_target(client, db):
    # Create a target first
    target = WebhookTarget(
        name="To Delete",
        url="https://example.com/webhook",
        secret="secret"
    )
    db.add(target)
    db.commit()
    
    response = client.delete(f"/api/v1/webhook-targets/{target.id}")
    assert response.status_code == 200
    
    # Verify deleted
    db_target = db.query(WebhookTarget).filter(WebhookTarget.id == target.id).first()
    assert db_target is None