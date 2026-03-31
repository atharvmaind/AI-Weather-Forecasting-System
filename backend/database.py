import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()

# Project root = parent of backend/
_ROOT = Path(__file__).resolve().parents[1]
_SQLITE_PATH = _ROOT / "data" / "weather.db"


def _default_sqlite_url() -> str:
    _SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # SQLAlchemy needs forward slashes in the URL on Windows too
    return f"sqlite:///{_SQLITE_PATH.as_posix()}"


# Local dev: SQLite by default (no PostgreSQL install required).
# Production (Render, etc.): set DATABASE_URL to your PostgreSQL connection string.
DATABASE_URL = os.getenv("DATABASE_URL") or _default_sqlite_url()

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
