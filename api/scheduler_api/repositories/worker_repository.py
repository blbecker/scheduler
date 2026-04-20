# scheduler_api/repositories/worker_repository.py
from typing import List, Optional
from scheduler_api.models import Worker
from sqlmodel import Session
import logging

logger = logging.getLogger(__name__)


class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Worker]:
        return self.session.query(Worker).all()

    def get_by_id(self, worker_id: int) -> Optional[Worker]:
        return self.session.get(Worker, worker_id)

    def add(self, worker: Worker) -> Worker:
        self.session.add(worker)
        self.session.commit()
        self.session.refresh(worker)
        return worker

    def update(self, worker: Worker) -> Optional[Worker]:
        existing_worker = self.session.get(Worker, worker.id)
        if existing_worker is None:
            return None
        worker_data = worker.model_dump(exclude_unset=True)
        for key, value in worker_data.items():
            setattr(existing_worker, key, value)
        self.session.add(existing_worker)
        self.session.commit()
        self.session.refresh(existing_worker)
        return existing_worker

    def delete(self, worker_id: int) -> bool:
        worker = self.session.get(Worker, worker_id)
        if worker is None:
            return False
        self.session.delete(worker)
        self.session.commit()
        return True
