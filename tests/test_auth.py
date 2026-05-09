import uuid

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_verify_rejects_without_token():
    r = client.get("/auth/verify")
    assert r.status_code == 401


def test_register_login_verify_flow():
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "secretpass123"

    r = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert r.status_code == 201
    assert r.json()["email"] == email

    r = client.post(
        "/auth/register",
        json={"email": email, "password": "othersecret1"},
    )
    assert r.status_code == 400

    r = client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpassword"},
    )
    assert r.status_code == 401

    r = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["user"]["email"] == email

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == email
