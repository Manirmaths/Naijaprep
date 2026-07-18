import os, sys
os.environ["DATABASE_URL"] = "sqlite:////tmp/npv/backend/pilot2.db"
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User

with TestClient(app) as client:
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin9").first():
        r = client.post("/api/auth/register", json={"username": "admin9", "email": "admin9@example.com", "password": "password123"})
        assert r.status_code == 201, r.text
        u = db.query(User).filter(User.username == "admin9").first()
        u.is_admin = True
        db.commit()
    if not db.query(User).filter(User.username == "stud9").first():
        r = client.post("/api/auth/register", json={"username": "stud9", "email": "stud9@example.com", "password": "password123"})
        assert r.status_code == 201, r.text
    db.close()

    # admin: check status table shows all 10 Math topics as draft, note_id set
    client.post("/api/auth/login", json={"email": "admin9@example.com", "password": "password123"})
    r = client.get("/api/admin/notes/status")
    assert r.status_code == 200, r.text
    rows = [x for x in r.json() if x["subject"] == "Mathematics"]
    assert len(rows) == 10, f"expected 10 Math topics, got {len(rows)}: {[x['topic'] for x in rows]}"
    for row in rows:
        assert row["status"] == "draft", row
        assert row["note_id"] is not None, row
    print("admin status table: 10/10 Math topics present as drafts, note_id set OK")

    # student can't see a draft note
    client.post("/api/auth/login", json={"email": "stud9@example.com", "password": "password123"})
    r = client.get("/api/notes/Mathematics/Algebraic Processes")
    assert r.status_code == 404, r.text
    print("draft correctly hidden from students OK")

    # admin publishes all 10
    client.post("/api/auth/login", json={"email": "admin9@example.com", "password": "password123"})
    for row in rows:
        r = client.put(f"/api/admin/notes/{row['note_id']}", json={"status": "active"})
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "active"
    print("all 10 published OK")

    # student reads each, marks read, checks glossary/related_topics/content present
    client.post("/api/auth/login", json={"email": "stud9@example.com", "password": "password123"})
    for row in rows:
        topic = row["topic"]
        r = client.get(f"/api/notes/Mathematics/{topic}")
        assert r.status_code == 200, (topic, r.text)
        note = r.json()
        assert len(note["content_md"]) > 200, (topic, "content too short")
        assert len(note["glossary"]) >= 3, (topic, note["glossary"])
        assert note["is_read"] is False

        r = client.post(f"/api/notes/Mathematics/{topic}/read")
        assert r.status_code == 200, r.text
        assert r.json()["is_read"] is True
    print("all 10 notes readable + markable as read OK, content substantial, glossaries present")

    # related_topics all point to real Math topic names
    all_topic_names = {row["topic"] for row in rows}
    for row in rows:
        r = client.get(f"/api/notes/Mathematics/{row['topic']}")
        note = r.json()
        for rt in note["related_topics"]:
            assert rt in all_topic_names, f"{row['topic']}'s related_topics references unknown topic {rt!r}"
    print("all related_topics reference real Mathematics topic names OK")

    # learn hub shows 10/10 for Mathematics
    r = client.get("/api/notes/learn-hub")
    assert r.status_code == 200, r.text
    hub = r.json()
    math_progress = next(s for s in hub["subjects"] if s["subject"] == "Mathematics")
    assert math_progress["total_topics"] == 10, math_progress
    assert math_progress["read_topics"] == 10, math_progress
    assert math_progress["percentage"] == 100.0, math_progress
    print("learn hub: Mathematics 10/10 read OK")

    # feedback + tutor quota still work against real content
    r = client.post("/api/notes/Mathematics/Calculus/feedback", json={"is_helpful": True})
    assert r.status_code == 200 and r.json()["helpful_count"] == 1, r.text
    r = client.post("/api/notes/Mathematics/Calculus/tutor", json={"message": "explain the power rule simply"})
    assert r.status_code == 200, r.text
    print("feedback + tutor endpoints OK (tutor uses graceful fallback -- no OPENAI_API_KEY set here)")

    print("\nALL REAL-CONTENT VERIFICATION PASSED")
