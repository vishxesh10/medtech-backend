import json
import re
from fastapi import HTTPException


def clean_json_response(text: str) -> dict:
    """
    Clean and parse JSON from the Gemini AI response.
    
    Gemini sometimes wraps JSON inside markdown code blocks (```json ... ```) 
    or adds explanatory notes. This function safely strips formatting and 
    extracts a valid Python dictionary.
    """
    if not text or not str(text).strip():
        raise HTTPException(
            status_code=502,
            detail="AI service returned an empty response. Please try again with a clearer image.",
        )

    # 1. Clean markdown code fence markers (```json and ```)
    cleaned = str(text).strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

    # 2. Try direct JSON parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Fallback: Find outermost '{' and '}' if the model included extra text
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 4. If all parsing attempts fail, raise a helpful error
    raise HTTPException(
        status_code=502,
        detail="Could not parse valid prescription data from AI output. Please upload a clear prescription image.",
    )
