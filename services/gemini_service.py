import os
from google import genai
from google.genai import types

class GeminiService:
    def __init__(self):
        # Initialize the genai client
        self.client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

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
            model='gemini-2.5-flash',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return response.text
