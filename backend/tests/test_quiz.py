"""
Regular practice quiz flow (routers/quiz.py): start/answer/skip/finish.

No dedicated test file existed for this core flow before -- test_diagnostic.py
covers the diagnostic variant's answer loop, but not skip or finish, which
back the Quiz.tsx "Skip" button and the timeout-auto-submit fix.
"""

from app.models import Question


def _seed_questions(db_session, n=5, subject="Mathematics", topic="Algebra"):
    for i in range(n):
        db_session.add(Question(
            question_id=f"seed-quiz-{subject}-{i}",
            subject=subject,
            topic=topic,
            difficulty="easy",
            source="original",
            status="active",
            question_text=f"Sample question {i}?",
            option_a="A", option_b="B", option_c="C", option_d="D",
            correct_option="B",
            explanation="Because B is correct.",
        ))
    db_session.commit()


def _start(client, register_user, db_session, n=5):
    _seed_questions(db_session, n=n)
    register_user()
    resp = client.post("/api/quiz/start", json={"subject": "Mathematics", "n": n})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_skip_advances_without_recording_a_response(client, register_user, db_session):
    attempt = _start(client, register_user, db_session, n=5)
    attempt_id = attempt["attempt_id"]
    first_qid = attempt["current_question"]["id"]

    resp = client.post(f"/api/quiz/{attempt_id}/skip")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["current_index"] == 1
    assert body["score"] == 0
    assert body["finished"] is False
    assert body["current_question"]["id"] != first_qid

    # Skipped question shows up as unanswered (blank), not wrong, in results.
    results = client.get(f"/api/quiz/{attempt_id}/results")
    item = next(i for i in results.json()["items"] if i["question_id"] == first_qid)
    assert item["selected_option"] == ""
    assert item["is_correct"] is False


def test_skipping_the_last_question_finishes_the_attempt(client, register_user, db_session):
    # start_quiz clamps n to a minimum of 3 (see SECONDS_PER_QUESTION /
    # _time_limit_for callers in quiz.py), so the smallest attempt possible
    # is 3 questions -- skip all three to reach the "last skip finishes it"
    # case rather than assuming a 1-question attempt is reachable.
    attempt = _start(client, register_user, db_session, n=3)
    attempt_id = attempt["attempt_id"]

    for _ in range(2):
        resp = client.post(f"/api/quiz/{attempt_id}/skip")
        assert resp.status_code == 200, resp.text
        assert resp.json()["finished"] is False

    last = client.post(f"/api/quiz/{attempt_id}/skip")
    assert last.status_code == 200, last.text
    assert last.json()["finished"] is True

    # Skipping an already-finished attempt is rejected, same as answer_quiz.
    resp2 = client.post(f"/api/quiz/{attempt_id}/skip")
    assert resp2.status_code == 400


def test_cannot_skip_someone_elses_attempt(client, register_user, db_session):
    attempt = _start(client, register_user, db_session, n=3)
    attempt_id = attempt["attempt_id"]

    # A second account shouldn't be able to skip on the first user's attempt.
    client.post("/api/auth/logout")
    register_user(username="intruder", email="intruder@example.com")
    resp = client.post(f"/api/quiz/{attempt_id}/skip")
    assert resp.status_code == 404


def test_finish_marks_an_incomplete_attempt_finished(client, register_user, db_session):
    attempt = _start(client, register_user, db_session, n=5)
    attempt_id = attempt["attempt_id"]

    # Only answer one of five -- simulates the timer running out early.
    qid = attempt["current_question"]["id"]
    client.post(f"/api/quiz/{attempt_id}/answer", json={"question_id": qid, "selected_option": "B"})

    resp = client.post(f"/api/quiz/{attempt_id}/finish")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["finished"] is True
    assert body["current_question"] is None

    # Results should still be computable, unanswered questions counted blank.
    results = client.get(f"/api/quiz/{attempt_id}/results")
    assert results.status_code == 200
    assert results.json()["total"] == 5
    assert results.json()["score"] == 1


def test_finish_is_idempotent(client, register_user, db_session):
    attempt = _start(client, register_user, db_session, n=3)
    attempt_id = attempt["attempt_id"]

    first = client.post(f"/api/quiz/{attempt_id}/finish")
    assert first.status_code == 200
    second = client.post(f"/api/quiz/{attempt_id}/finish")
    assert second.status_code == 200
    assert second.json()["finished"] is True


def test_finishing_a_diagnostic_early_still_sets_has_taken_diagnostic(client, register_user, db_session):
    from app.subjects import SUBJECTS

    for subject in SUBJECTS:
        _seed_questions(db_session, n=3, subject=subject, topic=f"{subject} topic")
    register_user()

    start = client.post("/api/quiz/start-diagnostic")
    assert start.status_code == 200, start.text
    attempt_id = start.json()["attempt_id"]

    dash_before = client.get("/api/dashboard").json()
    assert dash_before["has_taken_diagnostic"] is False

    client.post(f"/api/quiz/{attempt_id}/finish")

    dash_after = client.get("/api/dashboard").json()
    assert dash_after["has_taken_diagnostic"] is True
