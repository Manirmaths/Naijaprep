"""Throwaway smoke test for the mock-exam free-navigation flow -- run from /tmp/npv/backend."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./smoke_mock_nav.db"
os.environ["SECRET_KEY"] = "test-secret"

import sys
sys.path.insert(0, ".")

if os.path.exists("smoke_mock_nav.db"):
    os.remove("smoke_mock_nav.db")

from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    r = client.post("/api/auth/register", json={"username": "mocknav", "email": "mocknav@test.com", "password": "password123"})
    assert r.status_code == 201, r.text
    print("auth OK")

    from app.database import SessionLocal
    from app.models import Question
    db = SessionLocal()
    subjects_needed = [("English", 60)] + [(s, 40) for s in ["Mathematics", "Physics", "Chemistry"]]
    for subj, count in subjects_needed:
        for i in range(count):
            db.add(Question(
                question_id=f"{subj[:3].upper()}-{i:04d}", subject=subj, topic=f"{subj} Topic",
                question_text=f"{subj} Q{i}?", option_a="A opt", option_b="B opt",
                option_c="C opt", option_d="D opt", correct_option="B",
                explanation="Because.", status="active",
            ))
    db.commit()
    db.close()
    print("seeded question bank for mock exam")

    r = client.post("/api/mock/start", json={"subjects": ["Mathematics", "Physics", "Chemistry"]})
    assert r.status_code == 200, r.text
    attempt = r.json()
    attempt_id = attempt["attempt_id"]
    assert attempt["total"] == 180, attempt["total"]
    print("mock start OK, attempt_id =", attempt_id, "total =", attempt["total"])

    # Nav should show all 180 as unanswered, unmarked
    r = client.get(f"/api/mock/{attempt_id}/nav")
    assert r.status_code == 200, r.text
    nav = r.json()
    assert len(nav["items"]) == 180
    assert all(not it["answered"] and not it["marked"] for it in nav["items"])
    print("initial nav OK: 180 items, all unanswered/unmarked")

    # Fetch question at index 5, out of order (no sequential requirement)
    r = client.get(f"/api/mock/{attempt_id}/question/5")
    assert r.status_code == 200, r.text
    q5 = r.json()
    assert q5["index"] == 5 and q5["selected_option"] is None
    print("out-of-order question fetch OK")

    # Answer question 5
    r = client.put(f"/api/mock/{attempt_id}/answer/5", json={"selected_option": "B"})
    assert r.status_code == 204, r.text

    # Answer question 100 (jump far ahead)
    r = client.put(f"/api/mock/{attempt_id}/answer/100", json={"selected_option": "A"})
    assert r.status_code == 204, r.text

    # Re-fetch question 5 -- should now show the saved answer
    r = client.get(f"/api/mock/{attempt_id}/question/5")
    assert r.json()["selected_option"] == "B"
    print("answer persistence across navigation OK")

    # Mark question 5 for review
    r = client.put(f"/api/mock/{attempt_id}/mark/5")
    assert r.status_code == 204, r.text
    r = client.get(f"/api/mock/{attempt_id}/nav")
    nav = r.json()
    item5 = next(it for it in nav["items"] if it["index"] == 5)
    assert item5["marked"] is True and item5["answered"] is True
    print("mark for review OK")

    # Unmark
    r = client.put(f"/api/mock/{attempt_id}/mark/5")
    assert r.status_code == 204, r.text
    r = client.get(f"/api/mock/{attempt_id}/nav")
    item5 = next(it for it in r.json()["items"] if it["index"] == 5)
    assert item5["marked"] is False
    print("unmark OK")

    # Change the answer for question 5 (re-answer)
    r = client.put(f"/api/mock/{attempt_id}/answer/5", json={"selected_option": "C"})
    assert r.status_code == 204, r.text
    r = client.get(f"/api/mock/{attempt_id}/question/5")
    assert r.json()["selected_option"] == "C"
    print("re-answering (changing selection) OK")

    # Clear an answer
    r = client.put(f"/api/mock/{attempt_id}/answer/100", json={"selected_option": None})
    assert r.status_code == 204, r.text
    r = client.get(f"/api/mock/{attempt_id}/nav")
    item100 = next(it for it in r.json()["items"] if it["index"] == 100)
    assert item100["answered"] is False
    print("clearing an answer OK")

    # Answer a good number more so score is deterministic; correct option is always "B"
    # 5 -> "C" (wrong), 100 -> cleared (unanswered). Answer everything else correctly.
    for i in range(180):
        if i in (5, 100):
            continue
        r = client.put(f"/api/mock/{attempt_id}/answer/{i}", json={"selected_option": "B"})
        assert r.status_code == 204, r.text

    # Submit
    r = client.post(f"/api/mock/{attempt_id}/submit")
    assert r.status_code == 200, r.text
    results = r.json()
    assert results["total"] == 180
    assert results["score"] == 178, f"expected 178 correct (180 - 2 wrong/unanswered), got {results['score']}"
    print("submit OK, score =", results["score"], "/", results["total"])

    # Submitting again should fail
    r = client.post(f"/api/mock/{attempt_id}/submit")
    assert r.status_code == 400, r.text
    print("double-submit correctly rejected")

    # Answering after submit should fail
    r = client.put(f"/api/mock/{attempt_id}/answer/10", json={"selected_option": "A"})
    assert r.status_code == 400, r.text
    print("answering after submit correctly rejected")

    # QuestionMastery rows should exist for all 180 questions now
    db = SessionLocal()
    from app.models import QuestionMastery
    count = db.query(QuestionMastery).count()
    assert count == 180, f"expected 180 mastery rows, got {count}"
    db.close()
    print("QuestionMastery rows created at submit time OK:", count)

    print("\nALL MOCK NAV SMOKE TESTS PASSED")
