from __future__ import annotations

import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()


class Settings:
    """
    Application configuration settings.
    Reads environment variables or provides safe default values for local development.
    """

    def __init__(self):
        # Refresh environment variables from .env without overriding test fixtures
        load_dotenv(override=False)

        # Basic App Information
        self.app_name = os.getenv("APP_NAME", "MedTech API")
        self.app_description = os.getenv(
            "APP_DESCRIPTION",
            "AI-Powered Medical Prescription Digitizer and Management Backend",
        )
        self.app_version = os.getenv("APP_VERSION", "1.0.0")

        # CORS Settings (Allow cross-origin requests from frontend)
        raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
        self.cors_allow_origins = [
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        ]

        # JWT Authentication Configuration
        self.jwt_secret_key = os.getenv(
            "JWT_SECRET_KEY", "dev-only-secret-key-change-in-production-12345"
        )
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
        )  # Default: 7 days

        # Database Configuration
        # 'memory' = uses in-memory database (mongomock), perfect for testing without MongoDB installed
        # 'mongodb' = connects to local or cloud MongoDB (e.g. MongoDB Atlas)
        self.database_mode = os.getenv("DATABASE_MODE", "memory").strip().lower()
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip()
        self.mongodb_database = os.getenv("MONGODB_DATABASE", "medtech").strip()

        # Google Gemini AI Configuration
        self.gemini_key = (os.getenv("GEMINI_KEY") or "").strip()
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

        # Optional Bearer Token
        self.api_bearer_token = os.getenv("API_BEARER_TOKEN")


def get_settings() -> Settings:
    """
    Returns current application settings.
    """
    return Settings()
