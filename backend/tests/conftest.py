"""
Shared pytest fixtures for the backend test suite.

Each test gets a fresh, throwaway SQLite database (a real DB, not a mock --
per naijaprep_project_overview, integration-style tests against the actual
ORM/schema are what this project wants, not mocked-out data access) so tests
never touch the developer's local naijaprep.db or production data.
"""

import os
import sys

# So `import app...` resolves the same way it does when uvicorn runs from
# backend/ as the working directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.rate_limit import limiter


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    # Rate limits are a production concern; a test hammering /login in a loop
    # (e.g. to check 401 on bad password across several cases) shouldn't
    # trip them and produce an unrelated 429.
    limiter.enabled = False
    # Deliberately NOT using `with TestClient(app) as c:` -- that form fires
    # the app's real ASGI lifespan/startup event, which calls
    # Base.metadata.create_all(bind=engine)/ensure_schema() against the real
    # module-level `engine` (bound to DATABASE_URL, e.g. the developer's
    # local naijaprep.db) rather than this fixture's in-memory test engine.
    # Plain instantiation skips lifespan entirely, so tests never touch a
    # real database file.
    c = TestClient(app)
    yield c
    limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture()
def register_user(client):
    def _register(username="student1", email="student1@example.com", password="password123"):
        resp = client.post(
            "/api/auth/register",
            json={"username": username, "email": email, "password": password},
        )
        assert resp.status_code == 201, resp.text
        return resp

    return _register


@pytest.fixture()
def admin_client(client, db_session):
    """A client that's authenticated as an admin user."""
    resp = client.post(
        "/api/auth/register",
        json={"username": "admin1", "email": "admin1@example.com", "password": "password123"},
    )
    assert resp.status_code == 201, resp.text

    from app.models import User
    user = db_session.query(User).filter(User.email == "admin1@example.com").first()
    user.is_admin = True
    db_session.commit()

    return client
