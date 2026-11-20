from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =========================================================
# USER & AUTHENTICATION MODELS
# =========================================================

class User(BaseModel):
    """Internal user model matching database document."""
    id: str
    email: str
    name: str | None = None
    hashed_password: str
    created_at: datetime


class RegisterBody(BaseModel):
    """Request payload for user registration."""
    name: str | None = Field(default=None, description="User full name (optional)")
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="User password (minimum 6 characters required)",
    )


class LoginBody(BaseModel):
    """Request payload for user login."""
    email: EmailStr = Field(..., description="Registered user email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Response returned upon successful login containing JWT access token."""
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    """Public user profile data returned to frontend (excludes sensitive password)."""
    id: str
    email: str
    name: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# =========================================================
# PRESCRIPTION MODELS
# =========================================================

class PrescriptionRecord(BaseModel):
    """Internal prescription record stored in MongoDB."""
    id: str
    filename: str | None = None
    extracted_json: str
    created_at: datetime
    user_id: str


class ExtractedPrescriptionResponse(BaseModel):
    """Response returned right after prescription image upload & AI extraction."""
    message: str = "Prescription extracted successfully"
    saved_id: str
    extracted_data: dict


class PrescriptionSummary(BaseModel):
    """Compact summary of a prescription for list views."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str | None = None
    created_at: datetime | None = None


class PrescriptionDetailResponse(BaseModel):
    """Full prescription details including the parsed AI medical data."""
    id: str
    filename: str | None = None
    created_at: datetime | None = None
    extracted_data: dict


# =========================================================
# GENERAL API RESPONSES
# =========================================================

class MessageResponse(BaseModel):
    """Standard simple message response for operations like delete."""
    message: str
    detail: str | None = None


class UserStatsResponse(BaseModel):
    """Quick statistics for the logged-in user dashboard."""
    user_id: str
    email: str
    total_prescriptions: int
