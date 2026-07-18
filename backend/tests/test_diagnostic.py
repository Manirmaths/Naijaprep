"""
Onboarding diagnostic (Phase 3): POST /api/quiz/start-diagnostic samples a
few questions per subject and, once the attempt is fully answered, flips
User.has_taken_diagnostic -- the flag already existed and was already read
by the dashboard, but nothing ever set it before this.
"""

from app.models import Question
from app.subjects import SUBJECTS


def _seed_full_bank(db_session, per_subject=5):
    """Enough active questions in every subject for a real diagnostic run."""
    i = 0
    for subject in SUBJECTS:
        for _ in range(per_subject):
            i += 1
            db_session.add(Question(
                question_id=f"seed-{i}",
                subject=subject,
                topic=f"{subject} topic",
                difficulty="easy",
                source="original",
                status="active",
                question_text=f"Sample question {i}?",
                option_a="A", option_b="B", option_c="C", option_d="D",
                correct_option="B",
                explanation="Because B is correct.",
            ))
    db_session.commit()


def test_start_diagnostic_requires_auth(client):
    resp = client.post("/api/quiz/start-diagnostic")
    assert resp.status_code == 401


def test_start_diagnostic_samples_across_subjects(client, register_user, db_session):
    _seed_full_bank(db_session)
    register_user(email="newbie@example.com")

    resp = client.post("/api/quiz/start-diagnostic")
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "diagnostic"
    assert body["total"] == 3 * len(SUBJECTS)  # DIAGNOSTIC_QUESTIONS_PER_SUBJECT * 11


def test_completing_diagnostic_sets_has_taken_diagnostic(client, register_user, db_session):
    _seed_full_bank(db_session)
    register_user(email="finisher@example.com")

    start = client.post("/api/quiz/start-diagnostic")
    attempt_id = start.json()["attempt_id"]

    # Dashboard should still say false mid-attempt.
    dash = client.get("/api/dashboard").json()
    assert dash["has_taken_diagnostic"] is False

    total = start.json()["total"]
    for _ in range(total):
        state = client.get(f"/api/quiz/{attempt_id}").json()
        qid = state["current_question"]["id"]
        r = client.post(f"/api/quiz/{attempt_id}/answer", json={"question_id": qid, "selected_option": "B"})
        assert r.status_code == 200

    dash = client.get("/api/dashboard").json()
    assert dash["has_taken_diagnostic"] is True


def test_cannot_retake_diagnostic(client, register_user, db_session):
    _seed_full_bank(db_session)
    register_user(email="onceonly@example.com")

    start = client.post("/api/quiz/start-diagnostic")
    attempt_id = start.json()["attempt_id"]
    total = start.json()["total"]
    for _ in range(total):
        state = client.get(f"/api/quiz/{attempt_id}").json()
        qid = state["current_question"]["id"]
        client.post(f"/api/quiz/{attempt_id}/answer", json={"question_id": qid, "selected_option": "B"})

    resp = client.post("/api/quiz/start-diagnostic")
    assert resp.status_code == 400
