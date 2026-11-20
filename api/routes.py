from __future__ import annotations

import io
import json
import logging
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from PIL import Image
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from config import get_settings
from database import get_db
from models.models import (
    ExtractedPrescriptionResponse,
    LoginBody,
    MessageResponse,
    PrescriptionDetailResponse,
    PrescriptionRecord,
    PrescriptionSummary,
    RegisterBody,
    TokenResponse,
    User,
    UserPublic,
    UserStatsResponse,
)
from services.gemini_service import GeminiService
from utils.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from utils.json_parser import clean_json_response

router = APIRouter()
logger = logging.getLogger("medtech.routes")


# Helper function to get GeminiService instance (allows easy mocking in unit tests)
def _get_gemini_service() -> GeminiService:
    return GeminiService()


# =====================================================================
# SYSTEM & HEALTH CHECK ROUTES
# =====================================================================

@router.get("/", tags=["system"])
def root():
    """
    Root endpoint: returns a welcome message and links to interactive API docs.
    """
    return {
        "status": "online",
        "message": "Welcome to MedTech AI Backend!",
        "documentation": "/docs",
        "version": get_settings().app_version,
    }


@router.get("/health", tags=["system"])
def health():
    """
    Health check endpoint to verify backend server status.
    """
    return {"status": "ok"}


@router.get("/version", tags=["system"])
def version():
    """
    Return API application name and current version.
    """
    settings = get_settings()
    return {"name": settings.app_name, "version": settings.app_version}


# =====================================================================
# USER AUTHENTICATION ROUTES (Register, Login, Me, Verify)
# =====================================================================

@router.post(
    "/auth/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
def register(body: RegisterBody, db: Database = Depends(get_db)) -> User:
    """
    Register a new user account.
    - Validates email format and uniqueness.
    - Ensures password is at least 6 characters.
    - Stores hashed password securely in MongoDB.
    """
    # 1. Clean and normalize email input
    email = body.email.strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address cannot be empty.",
        )

    # 2. Check if a user with this email already exists
    existing_user = db.users.find_one({"email": email})
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 3. Hash the password and prepare database record
    user_document = {
        "email": email,
        "name": body.name.strip() if body.name else None,
        "hashed_password": hash_password(body.password),
        "created_at": datetime.utcnow(),
    }

    # 4. Insert user into MongoDB
    try:
        result = db.users.insert_one(user_document)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 5. Return created user (password omitted by response_model)
    return User(id=str(result.inserted_id), **user_document)


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(
    body: LoginBody,
    response: Response,
    db: Database = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user with email and password.
    Returns a JWT access token and automatically sets it as an HTTP cookie.
    """
    # 1. Clean and normalize email
    email = body.email.strip().lower()
    if not email or not body.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required.",
        )

    # 2. Retrieve user record from database
    user_doc = db.users.find_one({"email": email})
    if user_doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 3. Verify password hash
    if not verify_password(body.password, user_doc.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 4. Create JWT access token
    settings = get_settings()
    token = create_access_token(
        user_id=str(user_doc["_id"]),
        email=user_doc["email"],
        settings=settings,
    )

    # 5. Automatically set token in HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to False for local HTTP development (True in production HTTPS)
        path="/",
    )

    return TokenResponse(access_token=token)


@router.post("/auth/logout", response_model=MessageResponse, tags=["auth"])
def logout(response: Response) -> MessageResponse:
    """
    Log out the user by clearing the authentication cookie.
    """
    response.delete_cookie(key="access_token", path="/")
    return MessageResponse(
        message="Logged out successfully",
        detail="Authentication cookie cleared.",
    )


@router.get("/auth/me", response_model=UserPublic, tags=["auth"])
def me(current: User = Depends(get_current_user)) -> User:
    """
    Get profile information for the currently authenticated user.
    """
    return current


@router.get("/auth/verify", tags=["auth"])
def verify(current: User = Depends(get_current_user)) -> dict:
    """
    Quick endpoint to verify if the client's Bearer token is still valid.
    """
    return {
        "ok": True,
        "user": {
            "id": current.id,
            "email": current.email,
            "name": current.name,
        },
    }


# =====================================================================
# PRESCRIPTION OCR & MANAGEMENT ROUTES
# =====================================================================

@router.post(
    "/extract-prescription",
    response_model=ExtractedPrescriptionResponse,
    tags=["prescriptions"],
)
async def extract_prescription(
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ExtractedPrescriptionResponse:
    """
    Upload a prescription image, run AI extraction using Google Gemini,
    and save the extracted medical details to MongoDB.
    """
    # 1. Validate file presence
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a prescription image file to upload.",
        )

    # 2. Validate file type (must be an image)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only image uploads are supported",
        )

    # 3. Read uploaded image bytes
    try:
        file_bytes = await file.read()
    except Exception as read_err:
        logger.error("Failed to read uploaded file: %s", read_err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read the uploaded file.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded image file is empty.",
        )

    # 4. Open and verify image format with Pillow
    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as img_err:
        logger.error("Invalid image format: %s", img_err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Please upload a valid PNG, JPG, or WEBP image.",
        )

    # 5. Extract prescription information using Gemini AI
    try:
        gemini_service = _get_gemini_service()
        ai_response_text = gemini_service.extract_prescription(image)
        extracted_json_data = clean_json_response(ai_response_text)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Failed extracting prescription: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract prescription",
        )

    # 6. Save prescription record in database linked to current user
    prescription_record = {
        "filename": file.filename or "upload.png",
        "extracted_json": json.dumps(extracted_json_data),
        "created_at": datetime.utcnow(),
        "user_id": current.id,
    }
    result = db.prescriptions.insert_one(prescription_record)

    # 7. Return structured extraction response
    return ExtractedPrescriptionResponse(
        message="Prescription extracted successfully",
        extracted_data=extracted_json_data,
        saved_id=str(result.inserted_id),
    )


@router.get(
    "/prescriptions",
    response_model=list[PrescriptionSummary],
    tags=["prescriptions"],
)
def list_prescriptions(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=200, description="Maximum records to return"),
    db: Database = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[PrescriptionRecord]:
    """
    Get a list of all prescriptions uploaded by the logged-in user.
    Results are sorted by newest first.
    """
    safe_limit = min(max(limit, 1), 200)
    safe_skip = max(skip, 0)

    documents = (
        db.prescriptions.find({"user_id": current.id})
        .sort("created_at", -1)
        .skip(safe_skip)
        .limit(safe_limit)
    )

    return [
        PrescriptionRecord(
            id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"},
        )
        for doc in documents
    ]


@router.get(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionDetailResponse,
    tags=["prescriptions"],
)
def get_prescription(
    prescription_id: str,
    db: Database = Depends(get_db),
    current: User = Depends(get_current_user),
) -> PrescriptionDetailResponse:
    """
    Get full details of a specific prescription by its ID.
    Only the owner of the prescription can view it.
    """
    # 1. Validate ID format
    try:
        object_id = ObjectId(prescription_id)
    except (InvalidId, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    # 2. Search document owned by current user
    document = db.prescriptions.find_one({"_id": object_id, "user_id": current.id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    # 3. Parse JSON string into dictionary
    try:
        parsed_data = json.loads(document.get("extracted_json", "{}"))
    except Exception:
        parsed_data = {}

    return PrescriptionDetailResponse(
        id=str(document["_id"]),
        filename=document.get("filename"),
        created_at=document.get("created_at"),
        extracted_data=parsed_data,
    )


@router.delete(
    "/prescriptions/{prescription_id}",
    response_model=MessageResponse,
    tags=["prescriptions"],
)
def delete_prescription(
    prescription_id: str,
    db: Database = Depends(get_db),
    current: User = Depends(get_current_user),
) -> MessageResponse:
    """
    Delete a prescription by its ID.
    Users can only delete their own prescriptions.
    """
    # 1. Validate ID format
    try:
        object_id = ObjectId(prescription_id)
    except (InvalidId, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    # 2. Delete the prescription document
    result = db.prescriptions.delete_one({"_id": object_id, "user_id": current.id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    return MessageResponse(
        message="Prescription deleted successfully",
        detail=f"Prescription ID {prescription_id} was removed.",
    )


@router.get(
    "/prescriptions/stats/summary",
    response_model=UserStatsResponse,
    tags=["prescriptions"],
)
def prescription_stats(
    db: Database = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserStatsResponse:
    """
    Get user prescription statistics (e.g., total count of prescriptions).
    """
    count = db.prescriptions.count_documents({"user_id": current.id})
    return UserStatsResponse(
        user_id=current.id,
        email=current.email,
        total_prescriptions=count,
    )
