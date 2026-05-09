from __future__ import annotations

import json
import logging
from datetime import datetime

import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import get_db
from models.models import PrescriptionRecord, User
from services.gemini_service import GeminiService
from utils.auth import get_current_user
from utils.json_parser import clean_json_response

router = APIRouter()
logger = logging.getLogger("medtech.prescription")


class ExtractedPrescriptionResponse(BaseModel):
    extracted_data: dict
    saved_id: int


class PrescriptionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str | None = None
    created_at: datetime | None = None


class PrescriptionDetailResponse(BaseModel):
    id: int
    filename: str | None = None
    created_at: datetime | None = None
    extracted_data: dict


def _get_gemini_service() -> GeminiService:
    return GeminiService()


@router.get("/prescriptions", response_model=list[PrescriptionSummary])
def list_prescriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[PrescriptionRecord]:
    lim = min(max(limit, 1), 200)
    return (
        db.query(PrescriptionRecord)
        .filter(PrescriptionRecord.user_id == current.id)
        .order_by(PrescriptionRecord.created_at.desc())
        .offset(max(skip, 0))
        .limit(lim)
        .all()
    )


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionDetailResponse)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> PrescriptionDetailResponse:
    row = db.get(PrescriptionRecord, prescription_id)
    if row is None or row.user_id != current.id:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return PrescriptionDetailResponse(
        id=row.id,
        filename=row.filename,
        created_at=row.created_at,
        extracted_data=json.loads(row.extracted_json),
    )


@router.post("/extract-prescription", response_model=ExtractedPrescriptionResponse)
async def extract_prescription(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ExtractedPrescriptionResponse:
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=415, detail="Only image uploads are supported")

        image = Image.open(io.BytesIO(await file.read()))

        response_text = _get_gemini_service().extract_prescription(image)

        clean_data = clean_json_response(response_text)

        record = PrescriptionRecord(
            filename=file.filename or "upload",
            extracted_json=json.dumps(clean_data),
            user_id=current.id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return ExtractedPrescriptionResponse(extracted_data=clean_data, saved_id=record.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed extracting prescription: %s", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to extract prescription")
