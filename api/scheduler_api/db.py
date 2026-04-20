import os
from sqlmodel import create_engine

from sqlmodel import Session

PG_HOST = os.getenv("PG_HOST", "db")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "scheduler_db")
PG_USER = os.getenv("PG_USER", "scheduler_user")
PG_PASS = os.getenv("PG_PASS", "scheduler_pass")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

_engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Session:
    # _initialize_db()
    with Session(_engine) as session:
        yield session
