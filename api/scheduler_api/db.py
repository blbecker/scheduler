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

# LazyLoad the instantiation of the engine and sessionlocal. Create them the ifirst type that get_session is called. AI!
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create tables if not exist (only during early dev)."""
    # SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return SessionLocal()
