import io
import uuid

from fastapi.testclient import TestClient
from PIL import Image

from app import app
from api import routes as routes_api

client = TestClient(app)


def _register_and_login(email: str) -> str:
    password = "secretpass123"
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_prescriptions_are_persisted_and_user_scoped(monkeypatch):
    class FakeGeminiService:
        def extract_prescription(self, image):
            return '{"medicine": "example"}'

    monkeypatch.setattr(routes_api, "_get_gemini_service", lambda: FakeGeminiService())
    owner_token = _register_and_login(f"owner_{uuid.uuid4().hex}@example.com")

    # 1. Upload valid image
    image_buffer = io.BytesIO()
    Image.new("RGB", (4, 4), color="white").save(image_buffer, format="PNG")
    response = client.post(
        "/extract-prescription",
        files={"file": ("prescription.png", image_buffer.getvalue(), "image/png")},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200
    saved_id = response.json()["saved_id"]
    assert len(saved_id) == 24

    # 2. List prescriptions
    headers = {"Authorization": f"Bearer {owner_token}"}
    response = client.get("/prescriptions", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["id"] == saved_id

    # 3. Get single prescription details
    response = client.get(f"/prescriptions/{saved_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["extracted_data"] == {"medicine": "example"}

    # 4. Another user cannot access the prescription (User Scoping)
    other_token = _register_and_login(f"other_{uuid.uuid4().hex}@example.com")
    response = client.get(
        f"/prescriptions/{saved_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404

    # 5. Delete prescription
    delete_response = client.delete(f"/prescriptions/{saved_id}", headers=headers)
    assert delete_response.status_code == 200

    # 6. Verify deleted prescription is no longer found
    response_after_delete = client.get(f"/prescriptions/{saved_id}", headers=headers)
    assert response_after_delete.status_code == 404


def test_prescription_validation_errors():
    token = _register_and_login(f"val_{uuid.uuid4().hex}@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reject non-image file uploads
    response = client.post(
        "/extract-prescription",
        files={"file": ("notes.txt", b"plain text data", "text/plain")},
        headers=headers,
    )
    assert response.status_code == 415
