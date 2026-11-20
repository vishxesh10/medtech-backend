import uuid

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_verify_rejects_without_token():
    client.cookies.clear()
    r = client.get("/auth/verify")
    assert r.status_code == 401


def test_register_login_verify_flow():
    client.cookies.clear()
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "secretpass123"

    # 1. Register new user with optional name
    r = client.post(
        "/auth/register",
        json={"name": "Test Fresher", "email": email, "password": password},
    )
    assert r.status_code == 201
    assert r.json()["email"] == email
    assert r.json().get("name") == "Test Fresher"

    # 2. Duplicate registration should be rejected
    r = client.post(
        "/auth/register",
        json={"email": email, "password": "othersecret1"},
    )
    assert r.status_code == 400

    # 3. Login with wrong password should fail
    r = client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpassword"},
    )
    assert r.status_code == 401

    # 4. Login with correct password
    r = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    # Verify cookie was set automatically
    assert "access_token" in r.cookies
    assert r.cookies["access_token"] == token

    # 5. Verify token endpoint with Bearer header
    r = client.get("/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["user"]["email"] == email

    # 6. Profile /auth/me endpoint using automatic Cookie (No Authorization header sent!)
    r_cookie = client.get("/auth/me")
    assert r_cookie.status_code == 200
    assert r_cookie.json()["email"] == email

    # 7. Logout clears the cookie
    r_logout = client.post("/auth/logout")
    assert r_logout.status_code == 200

    # 8. After clearing cookies, accessing protected route without header fails
    client.cookies.clear()
    r_unauth = client.get("/auth/me")
    assert r_unauth.status_code == 401


def test_register_validation_errors():
    # Password too short (minimum 6 characters required)
    r = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "123"},
    )
    assert r.status_code == 422

    # Invalid email format
    r = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert r.status_code == 422
