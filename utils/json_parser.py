import json
import re
from fastapi import HTTPException

def clean_json_response(text: str):
    # Strip markdown and potential whitespace
    text = re.sub(r'```json|```', '', text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")
