"""Pytest fixtures: in-memory SQLite app + test client."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """A TestClient wired to an in-memory SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Sign up + log in a user and return the Authorization header."""
    client.post(
        "/signup",
        json={"name": "Test", "email": "tester@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/login", json={"email": "tester@example.com", "password": "secret123"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
