from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.database import Database

from config import get_settings
from database import get_db
from models.models import User

# HTTP Bearer scheme for Authorization: Bearer <token>
_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt with a generated salt.
    """
    salt = bcrypt.gensalt(rounds=10)
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_bytes.decode("ascii")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify whether a plain text password matches the stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("ascii"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(*, user_id: str, email: str, settings: Any = None) -> str:
    """
    Create a signed JWT access token containing the user ID and expiration time.
    """
    if settings is None:
        settings = get_settings()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str, settings: Any = None) -> dict:
    """
    Decode and verify a JWT access token using the secret key.
    """
    if settings is None:
        settings = get_settings()

    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: Any = Depends(get_settings),
    db: Database = Depends(get_db),
) -> User:
    """
    FastAPI dependency to authenticate requests (Pure Functional).
    Supports BOTH:
    1. Authorization: Bearer <token> header (standard API / Swagger UI)
    2. 'access_token' cookie (browser automatic credentials)
    """
    if settings is None or not hasattr(settings, "jwt_secret_key"):
        settings = get_settings()

    token: str | None = None

    # Step 1: Check Authorization header first
    if credentials and credentials.credentials:
        token = credentials.credentials
    # Step 2: Fall back to HTTP cookie if header is not present
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    # Step 3: If no token found anywhere, reject request
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 4: Decode and validate JWT token
    try:
        payload = decode_token(token, settings)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = ObjectId(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your login session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 5: Retrieve user from database
    user_doc = db.users.find_one({"_id": user_id})
    if user_doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 6: Return User model
    return User(
        id=str(user_doc["_id"]),
        **{k: v for k, v in user_doc.items() if k != "_id"},
    )
