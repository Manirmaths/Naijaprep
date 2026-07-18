"""
Phase 5: guardian/family links -- a parent, guardian, or tutor links
themselves as a read-only watcher of a student's progress via a shareable
code. Generic by design (see routers/family.py) so it covers both "parent
watching one child" and "tutor watching several students" without a
separate role/classroom model.
"""


def test_get_my_code_requires_auth(client):
    resp = client.get("/api/family/my-code")
    assert resp.status_code == 401


def test_get_my_code_generates_and_persists(client, register_user):
    register_user(email="student1@example.com")
    first = client.get("/api/family/my-code").json()["code"]
    second = client.get("/api/family/my-code").json()["code"]
    assert first == second
    assert len(first) == 8


def test_regenerate_code_changes_it(client, register_user):
    register_user(email="student2@example.com")
    original = client.get("/api/family/my-code").json()["code"]
    regenerated = client.post("/api/family/my-code/regenerate").json()["code"]
    assert regenerated != original


def test_link_with_unknown_code_404s(client, register_user):
    register_user(email="guardian1@example.com")
    resp = client.post("/api/family/link", json={"code": "NOTAREAL"})
    assert resp.status_code == 404


def test_cannot_link_to_self(client, register_user):
    register_user(email="solouser@example.com")
    code = client.get("/api/family/my-code").json()["code"]
    resp = client.post("/api/family/link", json={"code": code})
    assert resp.status_code == 400


def test_full_link_and_summary_flow(client, register_user):
    # Student gets their code first.
    register_user(username="thestudent", email="thestudent@example.com")
    code = client.get("/api/family/my-code").json()["code"]
    client.post("/api/auth/logout")

    # Guardian registers, links via the code.
    register_user(username="theguardian", email="theguardian@example.com")
    link_resp = client.post("/api/family/link", json={"code": code})
    assert link_resp.status_code == 201
    body = link_resp.json()
    assert body["username"] == "thestudent"

    children = client.get("/api/family/children").json()
    assert len(children) == 1
    student_id = children[0]["id"]

    summary = client.get(f"/api/family/children/{student_id}/summary")
    assert summary.status_code == 200
    assert summary.json()["username"] == "thestudent"


def test_cannot_relink_same_student_twice(client, register_user):
    register_user(username="student3", email="student3@example.com")
    code = client.get("/api/family/my-code").json()["code"]
    client.post("/api/auth/logout")

    register_user(username="guardian3", email="guardian3@example.com")
    first = client.post("/api/family/link", json={"code": code})
    assert first.status_code == 201
    second = client.post("/api/family/link", json={"code": code})
    assert second.status_code == 400


def test_summary_403s_for_unlinked_student(client, register_user):
    register_user(username="privatestudent", email="privatestudent@example.com")
    client.post("/api/auth/logout")

    register_user(username="randomguardian", email="randomguardian@example.com")
    # Never linked -- shouldn't be able to see anything about this student,
    # not even confirm the ID exists.
    resp = client.get("/api/family/children/999999/summary")
    assert resp.status_code == 404


def test_unlink_removes_access(client, register_user):
    register_user(username="student4", email="student4@example.com")
    code = client.get("/api/family/my-code").json()["code"]
    client.post("/api/auth/logout")

    register_user(username="guardian4", email="guardian4@example.com")
    student_id = client.post("/api/family/link", json={"code": code}).json()["id"]

    unlink = client.delete(f"/api/family/children/{student_id}")
    assert unlink.status_code == 200

    summary = client.get(f"/api/family/children/{student_id}/summary")
    assert summary.status_code == 404
