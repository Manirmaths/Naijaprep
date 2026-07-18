"""
Lesson-notes admin flow: draft/publish gate and the publish-all bulk action
added this session (backend/app/routers/admin.py's POST /notes/publish-all).
"""

from app.models import LessonNote


def _make_note(db_session, subject="Mathematics", topic="Algebra", status="draft"):
    note = LessonNote(
        subject=subject,
        topic=topic,
        title=f"{topic} notes",
        summary="A short summary.",
        glossary=[{"term": "x", "definition": "a variable"}],
        content_md="## Overview\n\nSome content.",
        related_topics=[],
        status=status,
    )
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    return note


def test_publish_all_requires_admin(client):
    resp = client.post("/api/admin/notes/publish-all")
    assert resp.status_code == 401


def test_publish_all_rejects_non_admin(client, register_user):
    register_user(email="student@example.com")
    resp = client.post("/api/admin/notes/publish-all")
    assert resp.status_code == 403


def test_publish_all_flips_drafts_to_active(admin_client, db_session):
    n1 = _make_note(db_session, topic="Algebra", status="draft")
    n2 = _make_note(db_session, topic="Geometry", status="draft")
    n3 = _make_note(db_session, topic="Trigonometry", status="active")

    resp = admin_client.post("/api/admin/notes/publish-all")
    assert resp.status_code == 200
    assert resp.json() == {"published": 2}

    db_session.refresh(n1)
    db_session.refresh(n2)
    db_session.refresh(n3)
    assert n1.status == "active"
    assert n2.status == "active"
    assert n3.status == "active"  # was already active, untouched but still active


def test_publish_all_is_idempotent(admin_client, db_session):
    _make_note(db_session, topic="Algebra", status="draft")

    first = admin_client.post("/api/admin/notes/publish-all")
    assert first.json() == {"published": 1}

    second = admin_client.post("/api/admin/notes/publish-all")
    assert second.json() == {"published": 0}


def test_publish_all_respects_subject_filter(admin_client, db_session):
    _make_note(db_session, subject="Mathematics", topic="Algebra", status="draft")
    _make_note(db_session, subject="Physics", topic="Mechanics", status="draft")

    resp = admin_client.post("/api/admin/notes/publish-all", params={"subject": "Mathematics"})
    assert resp.status_code == 200
    assert resp.json() == {"published": 1}

    statuses = {
        (n.subject, n.topic): n.status
        for n in db_session.query(LessonNote).all()
    }
    assert statuses[("Mathematics", "Algebra")] == "active"
    assert statuses[("Physics", "Mechanics")] == "draft"


def test_publish_all_rejects_unknown_subject(admin_client):
    resp = admin_client.post("/api/admin/notes/publish-all", params={"subject": "Not A Real Subject"})
    assert resp.status_code == 404
