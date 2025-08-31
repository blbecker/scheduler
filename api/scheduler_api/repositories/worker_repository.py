# scheduler_api/repositories/worker_repository.py
from typing import List, Optional
from sqlmodel import select
from scheduler_api.models import Worker
from scheduler_api.db import get_session


class WorkerRepository:

    def get_all(self) -> List[Worker]:
        with get_session() as session:
            return session.query(Worker).all()

    def get_by_id(self, worker_id: int) -> Optional[Worker]:
        with get_session() as session:
            return session.get(Worker, worker_id)

    def add(self, worker: Worker) -> Worker:
        with get_session() as session:
            session.add(worker)
            session.commit()
            session.refresh(worker)
            return worker
