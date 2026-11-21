from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from dotenv import load_dotenv

# Load variables from .env file located alongside config.py
_env_file = Path(__file__).resolve().parent / ".env"
if _env_file.exists():
    load_dotenv(dotenv_path=_env_file, override=False)
else:
    load_dotenv(override=False)


def get_settings() -> SimpleNamespace:
    """
    Functional configuration loader.
    Reads environment variables directly without OOP class hierarchies.
    """
    load_dotenv(override=False)

    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
    cors_allow_origins = [
        origin.strip() for origin in raw_origins.split(",") if origin.strip()
    ]

    return SimpleNamespace(
        # Basic App Information
        app_name=os.getenv("APP_NAME", "MedTech API"),
        app_description=os.getenv(
            "APP_DESCRIPTION",
            "AI-Powered Medical Prescription Digitizer and Management Backend",
        ),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        # CORS Settings
        cors_allow_origins=cors_allow_origins,
        # JWT Configuration
        jwt_secret_key=os.getenv(
            "JWT_SECRET_KEY", "dev-only-secret-key-change-in-production-12345"
        ),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
        ),
        # Database Settings
        database_mode=os.getenv("DATABASE_MODE", "memory").strip().lower(),
        mongodb_url=os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip(),
        mongodb_database=os.getenv("MONGODB_DATABASE", "medtech").strip(),
        # Gemini AI Configuration
        gemini_key=(os.getenv("GEMINI_KEY") or "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
        api_bearer_token=os.getenv("API_BEARER_TOKEN"),
    )


# Functional alias for any type annotations
Settings = SimpleNamespace
