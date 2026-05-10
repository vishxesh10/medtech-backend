from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import get_settings

_settings = get_settings()
_database_url = _settings.database_url.strip()

# Render may provide a DATABASE_URL with the legacy postgres:// scheme.
# SQLAlchemy with Psycopg 3 requires postgresql+psycopg:// for that driver.
if _database_url.startswith("postgres://"):
    _database_url = _database_url.replace("postgres://", "postgresql+psycopg://", 1)

if _database_url.startswith("sqlite"):
    engine = create_engine(
        _database_url,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        _database_url,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
