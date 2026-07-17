"""Throwaway smoke test for case-insensitive email handling -- run from /tmp/npv/backend."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./smoke_email.db"
os.environ["SECRET_KEY"] = "test-secret"

import sys
sys.path.insert(0, ".")

if os.path.exists("smoke_email.db"):
    os.remove("smoke_email.db")

from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    # Register with mixed-case email
    r = client.post("/api/auth/register", json={
        "username": "caseuser", "email": "John@Example.com", "password": "password123",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "john@example.com", f"expected lowercased email, got {body['email']!r}"
    print("register lowercases email OK:", body["email"])

    client.post("/api/auth/logout")

    # Login with different casing than what was registered
    r = client.post("/api/auth/login", json={"email": "JOHN@EXAMPLE.COM", "password": "password123"})
    assert r.status_code == 200, r.text
    print("login with different casing OK")

    client.post("/api/auth/logout")
    r = client.post("/api/auth/login", json={"email": "john@example.com", "password": "password123"})
    assert r.status_code == 200, r.text
    print("login with lowercase OK")

    # Duplicate registration with different casing should be rejected
    r = client.post("/api/auth/register", json={
        "username": "otheruser", "email": "john@EXAMPLE.com", "password": "password123",
    })
    assert r.status_code == 400, r.text
    print("duplicate registration (different casing) correctly rejected:", r.json())

    # forgot-password should also normalize (shouldn't error regardless of casing)
    r = client.post("/api/auth/forgot-password", json={"email": "John@Example.COM"})
    assert r.status_code == 200, r.text
    print("forgot-password with mixed case OK")

# --- Test the migration function against pre-existing mixed-case rows ---
from app.database import SessionLocal, normalize_emails
from app.models import User

db = SessionLocal()
# Insert directly (bypassing the schema validator) to simulate old data
# that predates the lowercasing fix.
u1 = User(username="legacy1", email="Legacy@Old.com", password_hash="x")
u2 = User(username="legacy2", email="already@lower.com", password_hash="x")
# Two rows that WOULD collide after lowercasing -- migration should skip both, not crash.
u3 = User(username="dupe1", email="Dupe@Case.com", password_hash="x")
db.add_all([u1, u2, u3])
db.commit()
db.close()

# Force a case-variant duplicate directly via raw insert (skip ORM unique
# check timing) to simulate two legacy rows that only differ by case.
db = SessionLocal()
from sqlalchemy import text as sql_text
db.execute(sql_text("PRAGMA foreign_keys=OFF"))
db.execute(sql_text(
    "INSERT INTO user (username, email, password_hash, points, is_admin, current_streak, "
    "longest_streak, streak_freezes, daily_goal, has_taken_diagnostic, created_at) "
    "VALUES ('dupe2', 'dupe@case.com', 'x', 0, 0, 0, 0, 0, 50, 0, datetime('now'))"
))
db.commit()
db.close()

normalize_emails()

db = SessionLocal()
legacy1 = db.query(User).filter(User.username == "legacy1").first()
legacy2 = db.query(User).filter(User.username == "legacy2").first()
dupe1 = db.query(User).filter(User.username == "dupe1").first()
dupe2 = db.query(User).filter(User.username == "dupe2").first()

assert legacy1.email == "legacy@old.com", f"expected lowercased, got {legacy1.email!r}"
print("migration lowercases legacy row OK:", legacy1.email)
assert legacy2.email == "already@lower.com"
print("migration leaves already-lowercase row alone OK")

# The colliding pair should be left untouched (still mixed case / lowercase
# as originally inserted) rather than crashing the whole migration.
assert dupe1.email == "Dupe@Case.com", f"expected untouched due to collision, got {dupe1.email!r}"
assert dupe2.email == "dupe@case.com"
print("migration safely skips colliding pair without crashing OK:", dupe1.email, dupe2.email)

db.close()

# Running the migration again should be a safe no-op.
normalize_emails()
print("re-running migration is a no-op OK")

print("\nALL EMAIL-CASE SMOKE TESTS PASSED")
