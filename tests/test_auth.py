"""Tests for signup and login."""


def test_signup_success(client):
    resp = client.post(
        "/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_signup_duplicate_email(client):
    payload = {"name": "A", "email": "a@example.com", "password": "secret123"}
    client.post("/signup", json=payload)
    resp = client.post("/signup", json=payload)
    assert resp.status_code == 409


def test_signup_missing_field(client):
    resp = client.post("/signup", json={"name": "A", "email": "a@example.com"})
    assert resp.status_code == 422


def test_login_success(client):
    client.post(
        "/signup",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/login", json={"email": "bob@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post(
        "/signup",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/login", json={"email": "bob@example.com", "password": "wrongpass"}
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/login", json={"email": "nobody@example.com", "password": "secret123"}
    )
    assert resp.status_code == 401
