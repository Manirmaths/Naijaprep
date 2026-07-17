import os, sys, tempfile
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp()}.db"
os.environ.setdefault("JWT_SECRET", "test-secret")
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Question, User

with TestClient(app) as client:
    db = SessionLocal()
    # seed questions across 2 subjects/topics
    for i in range(10):
        db.add(Question(
            question_id=f"T-{i:03d}", subject="Mathematics", topic="Algebra",
            difficulty="medium", question_text=f"Q{i}", option_a="a", option_b="b",
            option_c="c", option_d="d", correct_option="A", status="active",
        ))
    for i in range(3):
        db.add(Question(
            question_id=f"S-{i:03d}", subject="English", topic="Comprehension",
            difficulty="medium", question_text=f"E{i}", option_a="a", option_b="b",
            option_c="c", option_d="d", correct_option="B", status="active",
        ))
    db.commit()
    db.close()

    # register + login
    r = client.post("/api/auth/register", json={"username": "tester1", "email": "T@Example.com", "password": "password123"})
    assert r.status_code == 201, r.text
    r = client.post("/api/auth/login", json={"email": "t@example.com", "password": "password123"})
    assert r.status_code == 200, r.text

    # flashcards: enough pool (cookie auth carried automatically by TestClient)
    r = client.get("/api/flashcards", params={"topic": "Algebra", "n": 5})
    assert r.status_code == 200, r.text
    data = r.json()
    assert len(data["items"]) == 5, data
    assert data["items"][0]["answer_text"].startswith("A."), data["items"][0]

    # flashcards: not enough pool -> 400
    r = client.get("/api/flashcards", params={"topic": "Comprehension"})
    assert r.status_code == 400, r.text

    # flashcards: no auth -> 401
    client.cookies.clear()
    r = client.get("/api/flashcards", params={"topic": "Algebra"})
    assert r.status_code == 401, r.text

    # public: question of the day, no auth needed
    r = client.get("/api/public/question-of-the-day")
    assert r.status_code == 200, r.text
    qotd = r.json()
    assert "question_text" in qotd and "correct_option" in qotd, qotd
    r2 = client.get("/api/public/question-of-the-day")
    assert r2.json() == qotd, "should be stable within the same day"

    # public: top students, no auth needed
    r = client.get("/api/public/top-students")
    assert r.status_code == 200, r.text
    top = r.json()
    assert any(e["username"] == "tester1" for e in top["entries"]), top

    print("ALL PASSED")
