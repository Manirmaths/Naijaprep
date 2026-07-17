import os, sys, tempfile
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp()}.db"
os.environ.pop("OPENAI_API_KEY", None)  # force the no-key fallback path for this test
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Question, User

with TestClient(app) as client:
    db = SessionLocal()
    for i in range(6):
        db.add(Question(
            question_id=f"MTH-{i:03d}", subject="Mathematics", topic="Algebra",
            difficulty="medium", question_text=f"Solve for x: {i}x = {i*2}",
            option_a="a", option_b="b", option_c="c", option_d="d",
            correct_option="A", status="active", explanation="Because algebra." if i % 2 == 0 else None,
        ))
    db.add(User(username="admintest", email="admin@example.com", password_hash="x", is_admin=True))
    db.commit()
    db.close()

    # student + admin accounts
    r = client.post("/api/auth/register", json={"username": "stud1", "email": "stud1@example.com", "password": "password123"})
    assert r.status_code == 201, r.text
    student_client = client  # cookie jar now has stud1

    # promote a second user to admin via direct DB flip (simplest path for a smoke test)
    from app.database import SessionLocal as SL
    db2 = SL()
    from app.models import User as U
    u = db2.query(U).filter(U.username == "stud1").first()
    stud_id = u.id
    db2.close()

    r = client.post("/api/auth/register", json={"username": "admin1", "email": "admin1@example.com", "password": "password123"})
    assert r.status_code == 201, r.text
    db3 = SL()
    a = db3.query(U).filter(U.username == "admin1").first()
    a.is_admin = True
    db3.commit()
    db3.close()

    # login as admin
    r = client.post("/api/auth/login", json={"email": "admin1@example.com", "password": "password123"})
    assert r.status_code == 200, r.text

    # admin: notes status shows "missing" for Algebra before generation
    r = client.get("/api/admin/notes/status")
    assert r.status_code == 200, r.text
    rows = r.json()
    algebra_row = next(x for x in rows if x["subject"] == "Mathematics" and x["topic"] == "Algebra")
    assert algebra_row["status"] == "missing", algebra_row
    assert algebra_row["question_count"] == 6, algebra_row

    # admin: generate (no OPENAI_API_KEY -> graceful fallback content, still saved as draft)
    r = client.post("/api/admin/notes/generate", json={"subject": "Mathematics", "topic": "Algebra"})
    assert r.status_code == 200, r.text
    note = r.json()
    assert note["status"] == "draft", note
    note_id = note["id"]

    # admin: status now shows draft
    r = client.get("/api/admin/notes/status")
    algebra_row = next(x for x in r.json() if x["subject"] == "Mathematics" and x["topic"] == "Algebra")
    assert algebra_row["status"] == "draft", algebra_row

    # student can't see a draft note yet
    r = client.post("/api/auth/login", json={"email": "stud1@example.com", "password": "password123"})
    assert r.status_code == 200, r.text
    r = client.get("/api/notes/Mathematics/Algebra")
    assert r.status_code == 404, r.text

    # admin edits + publishes
    r = client.post("/api/auth/login", json={"email": "admin1@example.com", "password": "password123"})
    r = client.put(f"/api/admin/notes/{note_id}", json={
        "title": "Algebra Basics", "content_md": "## Intro\nAlgebra is fun.\n\nExample 1: solve 2x=4, x=2.",
        "summary": "An intro to algebra.", "glossary": [{"term": "variable", "definition": "an unknown value"}],
        "related_topics": ["Quadratic Equations"], "status": "active",
    })
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "active"

    # now student can read it
    r = client.post("/api/auth/login", json={"email": "stud1@example.com", "password": "password123"})
    r = client.get("/api/notes/Mathematics/Algebra")
    assert r.status_code == 200, r.text
    note = r.json()
    assert note["title"] == "Algebra Basics"
    assert note["is_read"] is False
    assert note["my_feedback"] is None

    # mark as read
    r = client.post("/api/notes/Mathematics/Algebra/read")
    assert r.status_code == 200, r.text
    assert r.json()["is_read"] is True

    # learn hub reflects 1/10 read for Mathematics (10 canonical topics from data/questions.csv,
    # but here only "Algebra" exists in this test DB, so total_topics=1)
    r = client.get("/api/notes/learn-hub")
    assert r.status_code == 200, r.text
    hub = r.json()
    math_progress = next(s for s in hub["subjects"] if s["subject"] == "Mathematics")
    assert math_progress["total_topics"] == 1, math_progress
    assert math_progress["read_topics"] == 1, math_progress
    assert math_progress["percentage"] == 100.0, math_progress

    # feedback: thumbs up, then change to thumbs down
    r = client.post("/api/notes/Mathematics/Algebra/feedback", json={"is_helpful": True})
    assert r.status_code == 200, r.text
    assert r.json()["helpful_count"] == 1 and r.json()["unhelpful_count"] == 0
    r = client.post("/api/notes/Mathematics/Algebra/feedback", json={"is_helpful": False})
    assert r.status_code == 200, r.text
    assert r.json()["helpful_count"] == 0 and r.json()["unhelpful_count"] == 1
    assert r.json()["my_feedback"] is False

    # tutor: no OPENAI_API_KEY -> graceful fallback string, still counts against quota
    r = client.post("/api/notes/Mathematics/Algebra/tutor", json={"message": "explain variables simply"})
    assert r.status_code == 200, r.text
    tutor_reply = r.json()
    assert "isn't set up" in tutor_reply["reply"], tutor_reply
    assert tutor_reply["queries_remaining_today"] == 29, tutor_reply

    # regenerate an already-active note without force -> rejected
    r = client.post("/api/auth/login", json={"email": "admin1@example.com", "password": "password123"})
    r = client.post("/api/admin/notes/generate", json={"subject": "Mathematics", "topic": "Algebra"})
    assert r.status_code == 400, r.text

    # regenerate with force -> allowed, resets to draft
    r = client.post("/api/admin/notes/generate", json={"subject": "Mathematics", "topic": "Algebra", "force": True})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "draft"

    print("ALL NOTES SMOKE TESTS PASSED")
