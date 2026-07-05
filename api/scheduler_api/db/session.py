# db/session.py
from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,  # Use SQLModel Session class
)


def init_db() -> None:
    pass  # keep for symmetry / future migrations


def get_session() -> Session:
    return SessionLocal()
