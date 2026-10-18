"""Tests for booking a class and viewing bookings."""

from datetime import datetime, timedelta


def _create_class(client, auth_headers, slots=2):
    future = (datetime.now() + timedelta(days=1)).isoformat()
    resp = client.post(
        "/classes",
        json={
            "name": "HIIT",
            "dateTime": future,
            "instructor": "Jane",
            "availableSlots": slots,
        },
        headers=auth_headers,
    )
    return resp.json()["id"]


def test_book_requires_auth(client):
    resp = client.post(
        "/book",
        json={"class_id": 1, "client_name": "A", "client_email": "a@example.com"},
    )
    assert resp.status_code == 401


def test_book_success_decrements_slots(client, auth_headers):
    class_id = _create_class(client, auth_headers, slots=2)
    resp = client.post(
        "/book",
        json={
            "class_id": class_id,
            "client_name": "Alice",
            "client_email": "alice@example.com",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["class_id"] == class_id

    listing = client.get("/classes", headers=auth_headers).json()
    created = next(c for c in listing if c["id"] == class_id)
    assert created["availableSlots"] == 1


def test_overbooking_blocked(client, auth_headers):
    class_id = _create_class(client, auth_headers, slots=1)
    # Need two different users to book the same class
    client.post(
        "/signup",
        json={"name": "U2", "email": "u2@example.com", "password": "secret123"},
    )
    t2 = client.post(
        "/login", json={"email": "u2@example.com", "password": "secret123"}
    ).json()["access_token"]

    # First user takes the only slot
    r1 = client.post(
        "/book",
        json={
            "class_id": class_id,
            "client_name": "Alice",
            "client_email": "alice@example.com",
        },
        headers=auth_headers,
    )
    assert r1.status_code == 201

    # Second user should be rejected
    r2 = client.post(
        "/book",
        json={
            "class_id": class_id,
            "client_name": "Bob",
            "client_email": "bob@example.com",
        },
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert r2.status_code == 409
    assert "fully booked" in r2.json()["detail"]


def test_duplicate_booking_blocked(client, auth_headers):
    class_id = _create_class(client, auth_headers, slots=10)
    payload = {
        "class_id": class_id,
        "client_name": "Alice",
        "client_email": "alice@example.com",
    }
    r1 = client.post("/book", json=payload, headers=auth_headers)
    assert r1.status_code == 201
    r2 = client.post("/book", json=payload, headers=auth_headers)
    assert r2.status_code == 409
    assert "already booked" in r2.json()["detail"]


def test_book_nonexistent_class(client, auth_headers):
    resp = client.post(
        "/book",
        json={
            "class_id": 9999,
            "client_name": "A",
            "client_email": "a@example.com",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_list_own_bookings(client, auth_headers):
    class_id = _create_class(client, auth_headers, slots=5)
    client.post(
        "/book",
        json={
            "class_id": class_id,
            "client_name": "Alice",
            "client_email": "alice@example.com",
        },
        headers=auth_headers,
    )
    resp = client.get("/bookings", headers=auth_headers)
    assert resp.status_code == 200
    bookings = resp.json()
    assert len(bookings) == 1
    assert bookings[0]["class_id"] == class_id
    assert bookings[0]["class_name"] == "HIIT"
