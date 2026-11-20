from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_root_welcome():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "online"
    assert "documentation" in body


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version():
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert "name" in body
    assert "version" in body


def test_auth_verify_requires_token():
    r = client.get("/auth/verify")
    assert r.status_code == 401
