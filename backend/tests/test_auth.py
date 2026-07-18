"""
Auth flow + permission-enforcement tests.

Covers the Phase 1 acceptance criterion "first pytest suite covering auth
(register/login/permission checks)". These exercise the real endpoints
through TestClient against a throwaway SQLite DB -- not mocked.
"""


def test_register_creates_user_and_sets_cookie(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "newstudent", "email": "newstudent@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "newstudent"
    assert body["email"] == "newstudent@example.com"
    # Admin must never be auto-granted on signup -- security-critical
    # invariant called out explicitly in routers/auth.py's own comment.
    assert body["is_admin"] is False
    assert "naijaprep_token" in resp.cookies


def test_register_rejects_duplicate_email(client, register_user):
    register_user(email="dupe@example.com")
    resp = client.post(
        "/api/auth/register",
        json={"username": "someoneelse", "email": "dupe@example.com", "password": "password123"},
    )
    assert resp.status_code == 400


def test_register_rejects_duplicate_username(client, register_user):
    register_user(username="dupeuser", email="first@example.com")
    resp = client.post(
        "/api/auth/register",
        json={"username": "dupeuser", "email": "second@example.com", "password": "password123"},
    )
    assert resp.status_code == 400


def test_register_normalizes_email_case(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "caseuser", "email": "CaseUser@Example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "caseuser@example.com"


def test_register_rejects_short_password(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "shortpw", "email": "shortpw@example.com", "password": "short"},
    )
    assert resp.status_code == 422


def test_login_success(client, register_user):
    register_user(email="loginuser@example.com", password="password123")
    resp = client.post(
        "/api/auth/login",
        json={"email": "loginuser@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    assert "naijaprep_token" in resp.cookies


def test_login_wrong_password_rejected(client, register_user):
    register_user(email="loginuser2@example.com", password="password123")
    resp = client.post(
        "/api/auth/login",
        json={"email": "loginuser2@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_email_rejected(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "nosuchuser@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


def test_me_requires_authentication(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user_when_logged_in(client, register_user):
    register_user(email="me@example.com")
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


def test_logout_clears_session(client, register_user):
    register_user(email="logout@example.com")
    assert client.get("/api/auth/me").status_code == 200

    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    assert client.get("/api/auth/me").status_code == 401


def test_forgot_password_gives_generic_response_for_unknown_email(client):
    # Must not reveal whether the email has an account -- see routers/auth.py.
    resp = client.post("/api/auth/forgot-password", json={"email": "ghost@example.com"})
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_admin_endpoint_requires_admin(client, register_user):
    register_user(email="regular@example.com")
    resp = client.get("/api/admin/stats")
    assert resp.status_code == 403


def test_admin_endpoint_rejects_anonymous(client):
    resp = client.get("/api/admin/stats")
    assert resp.status_code == 401


def test_admin_endpoint_allows_admin(admin_client):
    resp = admin_client.get("/api/admin/stats")
    assert resp.status_code == 200
