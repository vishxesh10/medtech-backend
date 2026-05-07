from fastapi import APIRouter, UploadFile, File
from PIL import Image
import io
import traceback
from services.gemini_service import GeminiService
from utils.json_parser import clean_json_response

router = APIRouter()
gemini_service = GeminiService()

@router.post("/extract-prescription")
async def extract_prescription(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read()))
        
        # Get raw response string from Gemini
        response_text = gemini_service.extract_prescription(image)
        
        # Clean and parse it
        clean_data = clean_json_response(response_text)
        
        return {"extracted_data": clean_data}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}
