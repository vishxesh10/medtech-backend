from config import get_settings

class GeminiService:
    def __init__(self):
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "Missing dependency for Gemini. Install `google-genai` to enable AI extraction."
            ) from e

        self._types = types

        settings = get_settings()
        if not settings.gemini_key:
            raise RuntimeError("Missing GEMINI_KEY. Set it in your environment or .env file.")

        self.model = settings.gemini_model
        self.client = genai.Client(api_key=settings.gemini_key)

    def extract_prescription(self, image) -> str:
        prompt = """
        You are a medical data extraction assistant. 
        Extract data from this image into a JSON object with this exact structure:
        {
            "patient_name": "string (or null)",
            "date": "YYYY-MM-DD",
            "medications": [
                {"name": "string", "dosage": "string", "frequency": "string", "duration": "string"}
            ]
        }
        Rules:
        1. If a field is missing, use null.
        2. Respond with ONLY the JSON. No conversational text.
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt, image],
            config=self._types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return response.text
