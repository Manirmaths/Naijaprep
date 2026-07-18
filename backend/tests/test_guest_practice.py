"""
Guest (unauthenticated) practice endpoint added for Phase 2's guest flow.
No login wall, so these tests double as the "does this leak more than it
should" check -- e.g. confirming the cap and the unknown-subject 404.
"""

from app.models import Question


def _make_question(db_session, subject="Mathematics", topic="Algebra", qid_suffix="1"):
    q = Question(
        question_id=f"mth-{qid_suffix}",
        subject=subject,
        topic=topic,
        difficulty="easy",
        source="original",
        status="active",
        question_text="What is 2 + 2?",
        option_a="3", option_b="4", option_c="5", option_d="6",
        correct_option="B",
        explanation="2 + 2 = 4.",
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    return q


def test_guest_practice_requires_no_auth(client, db_session):
    _make_question(db_session)
    resp = client.get("/api/public/guest-practice", params={"subject": "Mathematics"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["subject"] == "Mathematics"
    assert len(body["questions"]) == 1
    assert body["questions"][0]["correct_option"] == "B"


def test_guest_practice_rejects_unknown_subject(client):
    resp = client.get("/api/public/guest-practice", params={"subject": "Not A Real Subject"})
    assert resp.status_code == 404


def test_guest_practice_404_when_no_questions(client):
    resp = client.get("/api/public/guest-practice", params={"subject": "Physics"})
    assert resp.status_code == 404


def test_guest_practice_caps_at_max_n(client, db_session):
    for i in range(15):
        _make_question(db_session, qid_suffix=str(i))
    resp = client.get("/api/public/guest-practice", params={"subject": "Mathematics"})
    assert resp.status_code == 200
    assert len(resp.json()["questions"]) == 10  # GUEST_PRACTICE_MAX_N
