from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict

    _ENV_PATH = Path(__file__).resolve().parent / ".env"

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=_ENV_PATH if _ENV_PATH.is_file() else ".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

        app_name: str = "MedTech API"
        app_description: str = "API for MedTech AI application"
        app_version: str = "0.1.0"

        cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])

        api_bearer_token: str | None = Field(default=None, validation_alias="API_BEARER_TOKEN")

        jwt_secret_key: str = Field(
            default="dev-only-change-JWT_SECRET_KEY-in-production",
            validation_alias="JWT_SECRET_KEY",
        )
        jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
        access_token_expire_minutes: int = Field(
            default=60 * 24 * 7,
            validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        )

        # PostgreSQL: postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
        # Fallback for local/tests without Postgres: sqlite:///./prescriptions.db
        database_url: str = Field(
            default="sqlite:///./prescriptions.db",
            validation_alias="DATABASE_URL",
        )

        gemini_key: str | None = Field(default=None, validation_alias="GEMINI_KEY")
        gemini_model: str = Field(default="gemini-2.5-flash")

except ModuleNotFoundError:  # pragma: no cover

    class Settings:
        def __init__(self):
            self.app_name = os.getenv("APP_NAME", "MedTech API")
            self.app_description = os.getenv("APP_DESCRIPTION", "API for MedTech AI application")
            self.app_version = os.getenv("APP_VERSION", "0.1.0")
            self.cors_allow_origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")]
            self.api_bearer_token = os.getenv("API_BEARER_TOKEN")
            self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-only-change-JWT_SECRET_KEY-in-production")
            self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
            self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///./prescriptions.db")
            self.gemini_key = os.getenv("GEMINI_KEY")
            self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@lru_cache
def get_settings() -> Settings:
    return Settings()

