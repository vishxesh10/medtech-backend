from __future__ import annotations

import logging
import time
from fastapi import HTTPException, status
from config import get_settings

logger = logging.getLogger("medtech.gemini")


class GeminiService:
    """
    Service to interact with Google Gemini AI for medical prescription OCR & extraction.
    """

    def __init__(self):
        settings = get_settings()

        # Step 1: Check if API key is provided
        if not settings.gemini_key or not settings.gemini_key.strip():
            logger.error("Gemini API key is missing.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key is missing. Please set GEMINI_KEY in your .env file to enable AI extraction.",
            )

        # Step 2: Import Google GenAI library safely
        try:
            from google import genai
            from google.genai import types
            self._types = types
            self.client = genai.Client(api_key=settings.gemini_key)
            self.model = settings.gemini_model
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

    def extract_prescription(self, image) -> str:
        """
        Send the uploaded prescription image to Gemini AI and return raw JSON text.
        """
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

        for attempt in range(3):
            try:
                logger.info("Sending prescription image to Gemini model: %s", self.model)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt, image],
                    config=self._types.GenerateContentConfig(
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
                is_unavailable = (
                    getattr(error, "code", None) == 503
                    or getattr(error, "status", None) == "UNAVAILABLE"
                )
                if is_unavailable and attempt < 2:
                    logger.warning(
                        "Gemini is temporarily unavailable; retrying attempt %s of 3.",
                        attempt + 2,
                    )
                    time.sleep(2**attempt)
                    continue

                logger.exception("Error during Gemini API call: %s", error)
                if is_unavailable:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Gemini AI is temporarily unavailable due to high demand. Please try again shortly.",
                    ) from error
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Gemini AI processing error: {str(error)}",
                ) from error
