"""Infrastructure-independent genetic-algorithm scheduling engine.

The engine is intentionally free of SQLModel, SQLAlchemy, FastAPI, Celery,
and ``scheduler_api.db`` imports. See the GA engine design for the full
architecture.
"""
