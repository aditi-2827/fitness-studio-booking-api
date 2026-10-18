"""Tests for class creation and listing."""

from datetime import datetime, timedelta

from app.utils.tz import now_ist_naive


def _future_dt(days=1):
    """A future ISO datetime string."""
    return (datetime.now() + timedelta(days=days)).isoformat()


def test_create_class_requires_auth(client):
    resp = client.post(
        "/classes",
        json={
            "name": "Yoga",
            "dateTime": _future_dt(),
            "instructor": "John",
            "availableSlots": 10,
        },
    )
    assert resp.status_code == 401


def test_create_and_list_class(client, auth_headers):
    resp = client.post(
        "/classes",
        json={
            "name": "Yoga Flow",
            "dateTime": "2030-06-15T10:00:00Z",
            "instructor": "John Doe",
            "availableSlots": 20,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Yoga Flow"
    assert data["availableSlots"] == 20
    # UTC 10:00 is stored as IST 15:30, then returned as UTC "Z" again
    assert data["dateTime"] == "2030-06-15T10:00:00Z"

    listing = client.get("/classes", headers=auth_headers)
    assert listing.status_code == 200
    assert any(c["id"] == data["id"] for c in listing.json())


def test_list_excludes_past_classes(client, auth_headers):
    # Create a class in the past
    past = (datetime.now() - timedelta(days=1)).isoformat()
    client.post(
        "/classes",
        json={
            "name": "Old Class",
            "dateTime": past,
            "instructor": "X",
            "availableSlots": 5,
        },
        headers=auth_headers,
    )
    listing = client.get("/classes", headers=auth_headers)
    assert listing.status_code == 200
    assert all(c["name"] != "Old Class" for c in listing.json())


def test_create_class_validation(client, auth_headers):
    # availableSlots must be >= 1
    resp = client.post(
        "/classes",
        json={
            "name": "Bad",
            "dateTime": _future_dt(),
            "instructor": "X",
            "availableSlots": 0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422
