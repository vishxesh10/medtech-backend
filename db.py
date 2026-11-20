"""
Backward-compatibility alias for the database module.
Allows imports like `from db import get_db`.
"""

from database.database import client, database, get_db

__all__ = ["client", "database", "get_db"]
