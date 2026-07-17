"""Throwaway smoke test for push notification endpoints -- run from /tmp/npv/backend."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./smoke_push.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["NOTIFICATIONS_CRON_SECRET"] = "test-cron-secret"

import sys
sys.path.insert(0, ".")

if os.path.exists("smoke_push.db"):
    os.remove("smoke_push.db")

from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    r = client.post("/api/auth/register", json={"username": "pushtest", "email": "push@test.com", "password": "password123"})
    assert r.status_code in (200, 201), r.text
    r = client.post("/api/auth/login", json={"email": "push@test.com", "password": "password123"})
    assert r.status_code == 200, r.text
    print("auth OK")

    # VAPID public key endpoint (no key configured -> configured: False)
    r = client.get("/api/notifications/vapid-public-key")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["configured"] is False
    print("vapid-public-key (unconfigured) OK:", body)

    # Subscribe
    r = client.post("/api/notifications/subscribe", json={
        "endpoint": "https://fcm.googleapis.com/fake/endpoint123",
        "keys": {"p256dh": "fake-p256dh", "auth": "fake-auth"},
    })
    assert r.status_code == 204, r.text
    print("subscribe OK")

    from app.database import SessionLocal
    from app.models import PushSubscription
    db = SessionLocal()
    count = db.query(PushSubscription).count()
    assert count == 1, f"expected 1 subscription, got {count}"
    db.close()
    print("PushSubscription row created OK")

    # Re-subscribing same endpoint should upsert, not duplicate
    r = client.post("/api/notifications/subscribe", json={
        "endpoint": "https://fcm.googleapis.com/fake/endpoint123",
        "keys": {"p256dh": "fake-p256dh-2", "auth": "fake-auth-2"},
    })
    assert r.status_code == 204, r.text
    db = SessionLocal()
    count = db.query(PushSubscription).count()
    assert count == 1, f"expected still 1 subscription after re-subscribe, got {count}"
    db.close()
    print("re-subscribe upsert OK (no duplicate)")

    # send-reminders without correct secret -> 403
    r = client.post("/api/notifications/send-reminders")
    assert r.status_code == 403, r.text
    print("send-reminders without secret correctly 403")

    r = client.post("/api/notifications/send-reminders", headers={"X-Cron-Secret": "wrong"})
    assert r.status_code == 403, r.text
    print("send-reminders with wrong secret correctly 403")

    # send-reminders with correct secret -> 200, but no VAPID key configured
    # so it should report 0 sent (not_configured -> silently skipped)
    r = client.post("/api/notifications/send-reminders", headers={"X-Cron-Secret": "test-cron-secret"})
    assert r.status_code == 200, r.text
    result = r.json()
    print("send-reminders with correct secret OK:", result)
    assert result["eligible_users"] == 1  # hasn't practiced today
    assert result["sent"] == 0  # VAPID not configured

    # Unsubscribe
    r = client.post("/api/notifications/unsubscribe", json={"endpoint": "https://fcm.googleapis.com/fake/endpoint123"})
    assert r.status_code == 204, r.text
    db = SessionLocal()
    count = db.query(PushSubscription).count()
    assert count == 0, f"expected 0 subscriptions after unsubscribe, got {count}"
    db.close()
    print("unsubscribe OK")

    print("\nALL PUSH SMOKE TESTS PASSED")
