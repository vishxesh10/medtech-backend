from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any
try:
    import mongomock
except ImportError:
    mongomock = None

from pymongo import MongoClient
from pymongo.database import Database

from config import get_settings

logger = logging.getLogger("medtech.database")
_settings = get_settings()

client: MongoClient | Any

if _settings.database_mode == "mongodb":
    print("\n" + "=" * 60)
    print(f"[DATABASE] Attempting to connect to MongoDB: {_settings.mongodb_url}")
    try:
        client = MongoClient(
            _settings.mongodb_url,
            serverSelectionTimeoutMS=4000,
            connectTimeoutMS=4000,
        )
        # Test connection by pinging the database
        client.admin.command("ping")
        print(f"[DATABASE] SUCCESS: Connected to MongoDB database '{_settings.mongodb_database}'!")
        print("=" * 60 + "\n")
    except Exception as exc:
        print("\n" + "!" * 60)
        print("[DATABASE WARNING] Could not connect to MongoDB Atlas!")
        print(f"Reason: {exc}")
        print("\nCommon fixes for Atlas:")
        print("1. Go to cloud.mongodb.com -> Network Access -> Add IP Address")
        print("2. Choose 'Allow Access from Anywhere' (0.0.0.0/0)")
        print("3. Check database user password in .env")
        print("\n--> FALLING BACK TO IN-MEMORY MODE (mongomock) so your server stays running!")
        print("!" * 60 + "\n")
        client = mongomock.MongoClient()
else:
    print("\n" + "=" * 60)
    print("[DATABASE NOTICE] Running in MEMORY mode (mongomock).")
    print("WARNING: Data is saved only in temporary RAM and NOT in real MongoDB!")
    print("To save data permanently to MongoDB Atlas, set DATABASE_MODE=mongodb in your .env file.")
    print("=" * 60 + "\n")
    client = mongomock.MongoClient()

database = client[_settings.mongodb_database]
_indexed_database: Database | None = None


def get_db() -> Generator[Database, None, None]:
    """
    FastAPI dependency to provide database session.
    Ensures required database indexes exist on first call.
    """
    global _indexed_database
    if _indexed_database is not database:
        try:
            # 1. Unique email index so duplicate user accounts cannot be created
            database.users.create_index("email", unique=True)
            # 2. Compound index on prescriptions for fast lookup by user and creation date
            database.prescriptions.create_index([("user_id", 1), ("created_at", -1)])
            _indexed_database = database
        except Exception as err:
            logger.warning("Index creation notice: %s", err)

    yield database
