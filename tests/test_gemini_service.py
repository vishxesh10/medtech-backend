from types import SimpleNamespace

import pytest
from google.genai.errors import ServerError
from fastapi import HTTPException

import services.gemini_service as gemini_service_module


class FakeModels:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    def generate_content(self, **kwargs):
        self.calls += 1
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def _service_with_responses(responses):
    service = gemini_service_module.GeminiService.__new__(
        gemini_service_module.GeminiService
    )
    service.client = SimpleNamespace(models=FakeModels(responses))
    service._types = SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs)
    service.model = "test-model"
    return service


def _unavailable_error():
    return ServerError(
        503,
        {
            "error": {
                "code": 503,
                "message": "Model is experiencing high demand.",
                "status": "UNAVAILABLE",
            }
        },
    )


def test_extract_prescription_retries_temporary_gemini_unavailability(monkeypatch):
    service = _service_with_responses(
        [_unavailable_error(), SimpleNamespace(text='{"medications": []}')]
    )
    delays = []
    monkeypatch.setattr(gemini_service_module.time, "sleep", delays.append)

    result = service.extract_prescription(object())

    assert result == '{"medications": []}'
    assert service.client.models.calls == 2
    assert delays == [1]


def test_extract_prescription_returns_503_after_retries_are_exhausted(monkeypatch):
    service = _service_with_responses(
        [_unavailable_error(), _unavailable_error(), _unavailable_error()]
    )
    delays = []
    monkeypatch.setattr(gemini_service_module.time, "sleep", delays.append)

    with pytest.raises(HTTPException) as exc_info:
        service.extract_prescription(object())

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == (
        "Gemini AI is temporarily unavailable due to high demand. Please try again shortly."
    )
    assert service.client.models.calls == 3
    assert delays == [1, 2]
