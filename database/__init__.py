"""
Database package exports.

Import from here to avoid depending on internal module paths.
"""

from .database import client, database, get_db

__all__ = ["client", "database", "get_db"]
