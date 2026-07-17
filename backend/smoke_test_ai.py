"""Throwaway smoke test for the adaptive-practice/AI features -- run from /tmp/npv/backend."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./smoke_ai.db"
os.environ["SECRET_KEY"] = "test-secret"

import sys
sys.path.insert(0, ".")

if os.path.exists("smoke_ai.db"):
    os.remove("smoke_ai.db")

from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    # Register + login
    r = client.post("/api/auth/register", json={"username": "smoketest", "email": "smoke@test.com", "password": "password123"})
    assert r.status_code in (200, 201), r.text
    r = client.post("/api/auth/login", json={"email": "smoke@test.com", "password": "password123"})
    assert r.status_code == 200, r.text
    print("auth OK")

    # Seed a couple of questions directly via DB session
    from app.database import SessionLocal
    from app.models import Question
    db = SessionLocal()
    qs = []
    for i in range(10):
        q = Question(
            question_id=f"SMK-{i:03d}", subject="Mathematics", topic="Algebra",
            question_text=f"What is {i} + 1?", option_a=str(i), option_b=str(i+1),
            option_c=str(i+2), option_d=str(i+3), correct_option="B",
            explanation="Because addition.", status="active",
        )
        db.add(q)
        qs.append(q)
    db.commit()
    for q in qs:
        db.refresh(q)
    qids = [q.id for q in qs]
    db.close()
    print(f"seeded {len(qids)} questions")

    # Dashboard should work pre-practice (score estimate not available yet)
    r = client.get("/api/dashboard")
    assert r.status_code == 200, r.text
    dash = r.json()
    assert dash["score_estimate"]["available"] is False
    assert dash["due_for_review_count"] == 0
    assert dash["recommended_topics"] == []
    print("dashboard OK (pre-practice)")

    # Start a normal quiz and answer a few -- mix correct/incorrect to
    # exercise QuestionMastery box logic
    r = client.post("/api/quiz/start", json={"subject": "Mathematics", "n": 5})
    assert r.status_code == 200, r.text
    attempt = r.json()
    attempt_id = attempt["attempt_id"]

    answered_qids = []
    for i in range(5):
        cur = attempt["current_question"]
        answered_qids.append(cur["id"])
        # answer correctly on evens, wrong on odds
        selected = "B" if i % 2 == 0 else "A"
        r = client.post(f"/api/quiz/{attempt_id}/answer", json={"question_id": cur["id"], "selected_option": selected})
        assert r.status_code == 200, r.text
        attempt = r.json()["next"]
    answered_qid = answered_qids[-1]
    print("answered quiz questions OK, answered:", answered_qids)

    # QuestionMastery rows should now exist
    db = SessionLocal()
    from app.models import QuestionMastery
    mastery_count = db.query(QuestionMastery).count()
    assert mastery_count == 5, f"expected 5 mastery rows, got {mastery_count}"
    db.close()
    print(f"QuestionMastery rows: {mastery_count} OK")

    # Smart review: due-count and start
    r = client.get("/api/smart-review/due-count")
    assert r.status_code == 200, r.text
    due = r.json()["due_count"]
    print(f"due_count = {due}")

    r = client.post("/api/smart-review/start", json={"n": 5})
    assert r.status_code == 200, r.text
    sr_attempt = r.json()
    assert sr_attempt["total"] > 0
    print(f"smart-review start OK, total={sr_attempt['total']}")

    # Dashboard due_for_review_count should reflect mastery rows (box 1 => next_review in 1 day, not due yet actually!)
    r = client.get("/api/dashboard")
    assert r.status_code == 200, r.text
    print("dashboard OK (post-practice) due_for_review_count =", r.json()["due_for_review_count"])

    # AI Tutor: ask about the last answered question (already answered -> allowed)
    r = client.post("/api/tutor/ask", json={"question_id": answered_qid, "message": "Can you explain this differently?"})
    assert r.status_code == 200, r.text
    tutor_resp = r.json()
    assert "not set up yet" in tutor_resp["reply"] or len(tutor_resp["reply"]) > 0
    print("tutor ask (no key) OK:", tutor_resp["reply"][:60])

    # AI Tutor: ask about a question NOT yet answered -> should 403
    unanswered = [qid for qid in qids if qid not in answered_qids][0]
    r = client.post("/api/tutor/ask", json={"question_id": unanswered, "message": "help"})
    assert r.status_code == 403, f"expected 403 for unanswered question, got {r.status_code}: {r.text}"
    print("tutor ask on unanswered question correctly 403 OK")

    # Admin suggest-tags (need admin user)
    db = SessionLocal()
    from app.models import User
    u = db.query(User).filter(User.email == "smoke@test.com").first()
    u.is_admin = True
    db.commit()
    db.close()

    r = client.post("/api/admin/suggest-tags", json={
        "question_text": "What is the capital of Nigeria?",
        "option_a": "Lagos", "option_b": "Abuja", "option_c": "Kano", "option_d": "Ibadan",
        "correct_option": "B",
    })
    assert r.status_code == 200, r.text
    print("admin suggest-tags (no key) OK:", r.json())

    print("\nALL SMOKE TESTS PASSED")
