"""
Phase 4: Paystack payments (initialize + webhook) and the first concrete
premium/free gate (free mock exam allowance on /api/mock/start).

No real Paystack calls happen in tests -- PAYSTACK_SECRET_KEY is unset in
the test environment (same as any unconfigured deployment), so /initialize
is expected to 501 rather than hit the network, and the webhook signature
tests exercise the HMAC verification logic directly.
"""

from datetime import datetime, timedelta

from app.config import settings
from app.models import QuizAttempt


def test_payment_status_requires_auth(client):
    resp = client.get("/api/payments/status")
    assert resp.status_code == 401


def test_payment_status_default_state(client, register_user):
    register_user(email="freeuser@example.com")
    resp = client.get("/api/payments/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_premium"] is False
    assert body["premium_until"] is None
    assert body["free_mock_exams_remaining"] == settings.FREE_MOCK_EXAMS


def test_initialize_requires_auth(client):
    resp = client.post("/api/payments/initialize")
    assert resp.status_code == 401


def test_initialize_without_paystack_key_returns_501(client, register_user):
    # Test env never sets PAYSTACK_SECRET_KEY -- same state as any
    # not-yet-configured deployment.
    register_user(email="wouldpay@example.com")
    resp = client.post("/api/payments/initialize")
    assert resp.status_code == 501


def test_webhook_rejects_missing_signature(client):
    resp = client.post("/api/payments/webhook", json={"event": "charge.success", "data": {}})
    assert resp.status_code == 401


def test_webhook_rejects_wrong_signature(client):
    resp = client.post(
        "/api/payments/webhook",
        json={"event": "charge.success", "data": {}},
        headers={"x-paystack-signature": "not-the-real-signature"},
    )
    assert resp.status_code == 401


def test_mock_start_blocked_after_free_quota(client, register_user, db_session):
    register_user(email="mockuser@example.com")
    from app.models import User
    user = db_session.query(User).filter(User.email == "mockuser@example.com").first()

    # Simulate the user having already used their one free mock, without
    # needing to seed a full 180-question bank to actually run one --
    # the premium gate in mock.py runs before any subject/question work.
    db_session.add(QuizAttempt(
        user_id=user.id, mode="mock", question_ids=[], current_index=0, score=0,
        time_limit_seconds=7200,
    ))
    db_session.commit()

    resp = client.post("/api/mock/start", json={"subjects": ["Physics", "Chemistry", "Biology"]})
    assert resp.status_code == 402


def test_mock_start_not_blocked_for_premium_user(client, register_user, db_session):
    register_user(email="premiumuser@example.com")
    from app.models import User
    user = db_session.query(User).filter(User.email == "premiumuser@example.com").first()
    user.premium_until = datetime.utcnow() + timedelta(days=10)
    db_session.add(QuizAttempt(
        user_id=user.id, mode="mock", question_ids=[], current_index=0, score=0,
        time_limit_seconds=7200,
    ))
    db_session.commit()

    # Empty question bank in this test -- the point is just confirming we get
    # PAST the premium gate (i.e. NOT a 402) and into real subject validation.
    resp = client.post("/api/mock/start", json={"subjects": ["Physics", "Chemistry", "Biology"]})
    assert resp.status_code != 402
