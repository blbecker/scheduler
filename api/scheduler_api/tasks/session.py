"""Database session management for Celery tasks."""

from sqlmodel import Session
from scheduler_api.db.session import SessionLocal


def get_task_session() -> Session:
    """Get a new database session for Celery tasks (same as FastAPI)."""
    return SessionLocal()
