# scheduler_api/repositories/worker_repository.py
from typing import List, Optional
from sqlmodel import select
from scheduler_api.models import Worker
from scheduler_api.db import get_session


class WorkerRepository:
    def _get_session(self):
        return get_session()

    def get_all(self) -> List[Worker]:
        with self._get_session() as session:
            stmt = select(Worker)
            return session.exec(stmt).all()

    def get_by_id(self, worker_id: int) -> Optional[Worker]:
        with self._get_session() as session:
            return session.get(Worker, worker_id)

    def add(self, worker: Worker) -> Worker:
        with self._get_session() as session:
            session.add(worker)
            session.commit()
            session.refresh(worker)
            return worker

    def update(self, worker: Worker) -> Optional[Worker]:
        with self._get_session() as session:
            existing_worker = session.get(Worker, worker.id)
            if existing_worker is None:
                return None
            worker_data = worker.dict(exclude_unset=True)
            for key, value in worker_data.items():
                setattr(existing_worker, key, value)
            session.add(existing_worker)
            session.commit()
            session.refresh(existing_worker)
            return existing_worker

    def delete(self, worker_id: int) -> bool:
        with self._get_session() as session:
            worker = session.get(Worker, worker_id)
            if worker is None:
                return False
            session.delete(worker)
            session.commit()
            return True
