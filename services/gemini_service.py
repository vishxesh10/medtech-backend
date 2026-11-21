from __future__ import annotations

import logging
from types import SimpleNamespace
from fastapi import HTTPException, status
from config import get_settings

logger = logging.getLogger("medtech.gemini")


def extract_prescription(image) -> str:
    """
    Pure functional handler to send prescription image to Gemini AI and return raw JSON.
    No classes, no self, no OOP boilerplate.
    """
    settings = get_settings()

    # Step 1: Validate API key presence
    if not settings.gemini_key or not settings.gemini_key.strip():
        logger.error("Gemini API key is missing.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gemini API key is missing. Please set GEMINI_KEY in your .env file to enable AI extraction.",
        )

    # Step 2: Initialize Google GenAI client
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.gemini_key)
        model = settings.gemini_model
    except ImportError as err:
        logger.error("google-genai library is not installed: %s", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google GenAI library is not installed. Please run 'pip install google-genai'.",
        )
    except Exception as exc:
        logger.error("Failed to initialize Gemini client: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Gemini client: {str(exc)}",
        )

    # Step 3: Medical extraction prompt
    prompt = """
    You are an intelligent medical document assistant.
    Analyze this medical prescription image carefully and extract all information into a JSON object.

    Return JSON matching this exact structure:
    {
        "patient_name": "string (or null if not found)",
        "doctor_name": "string (or null if not found)",
        "date": "YYYY-MM-DD (or as written on the prescription, or null)",
        "diagnosis": "string (or null if not mentioned)",
        "medications": [
            {
                "name": "Medication name",
                "dosage": "e.g. 500mg, 10ml (or null)",
                "frequency": "e.g. 1-0-1, Once daily, Twice daily (or null)",
                "duration": "e.g. 5 days, 1 week (or null)",
                "instructions": "e.g. After food, Before breakfast (or null)"
            }
        ],
        "advice": "General advice or instructions given by the doctor (or null)"
    }

    Strict Rules:
    1. If a value is missing or unreadable, set its value to null.
    2. Always return a valid JSON object. Do not include markdown preamble, greeting, or conversational text.
    """

    try:
        logger.info("Sending prescription image to Gemini model: %s", model)
        response = client.models.generate_content(
            model=model,
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        if not response or not response.text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini AI returned an empty response. Please verify the image clarity.",
            )
        return response.text
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Error during Gemini API call: %s", error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini AI processing error: {str(error)}",
        )


# Functional service adapter for backward compatibility with route calls & unit tests
def GeminiService():
    """Returns a functional namespace exposing extract_prescription."""
    return SimpleNamespace(extract_prescription=extract_prescription)
