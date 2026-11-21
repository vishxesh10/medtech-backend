from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException

import services.gemini_service as gemini_service_module


def test_extract_prescription_missing_key(monkeypatch):
    monkeypatch.setattr(
        gemini_service_module,
        "get_settings",
        lambda: SimpleNamespace(gemini_key="", gemini_model="gemini-2.5-flash"),
    )
    with pytest.raises(HTTPException) as exc_info:
        gemini_service_module.extract_prescription(object())

    assert exc_info.value.status_code == 400
    assert "Gemini API key is missing" in exc_info.value.detail


def test_extract_prescription_success(monkeypatch):
    monkeypatch.setattr(
        gemini_service_module,
        "get_settings",
        lambda: SimpleNamespace(gemini_key="fake-key-123", gemini_model="gemini-2.5-flash"),
    )

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"medications": [{"name": "Paracetamol"}]}'
    mock_client.models.generate_content.return_value = mock_response

    mock_genai = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_genai.types.GenerateContentConfig = MagicMock()

    mock_google = MagicMock()
    mock_google.genai = mock_genai

    with patch.dict("sys.modules", {"google": mock_google, "google.genai": mock_genai, "google.genai.types": mock_genai.types}):
        result = gemini_service_module.extract_prescription(object())
        assert "Paracetamol" in result
