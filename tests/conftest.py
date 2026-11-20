from __future__ import annotations

import os
from importlib import import_module

# Force in-memory database and test secret for all automated tests
os.environ["DATABASE_MODE"] = "memory"
os.environ.setdefault("MONGODB_DATABASE", "medtech_test")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-jwt-secret-key-minimum-32-characters-long!",
)

import mongomock
import pytest


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    """
    Session-wide fixture that initializes an in-memory mongomock database.
    """
    database_module = import_module("database.database")
    client = mongomock.MongoClient()
    database_module.database = client["medtech_test"]
    database_module._indexed_database = None
    yield
    client.close()
