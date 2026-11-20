"""Infrastructure-independent genetic-algorithm scheduling engine.

The engine is intentionally free of SQLModel, SQLAlchemy, FastAPI, Celery,
and ``scheduler_api.db`` imports. See the GA engine design for the full
architecture.

Shared helpers ``exceptions``, ``ranking``, ``randomness``, and ``validation``
are the only non-model engine modules that components and aggregation may
import. They must not depend on protocols, execution, controller, or solver.
"""
