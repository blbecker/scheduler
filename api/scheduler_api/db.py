import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlmodel import SQLModel

PG_HOST = os.getenv("PG_HOST", "db")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "scheduler_db")
PG_USER = os.getenv("PG_USER", "scheduler_user")
PG_PASS = os.getenv("PG_PASS", "scheduler_pass")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

_engine = None
_SessionLocal = None


def _initialize_db():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = create_engine(DATABASE_URL, echo=True, future=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def init_db() -> None:
    _initialize_db()
    # SQLModel.metadata.create_all(_engine)


def get_session() -> Session:
    _initialize_db()
    return _SessionLocal()
