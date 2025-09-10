# scheduler_api/repositories/worker_repository.py
from typing import List, Optional
from scheduler_api.models import Worker
from sqlmodel import Session


class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Worker]:
        with self.session as session:
            return session.query(Worker).all()

    def get_by_id(self, worker_id: int) -> Optional[Worker]:
        with self.session as session:
            return session.get(Worker, worker_id)

    def add(self, worker: Worker) -> Worker:
        with self.session as session:
            session.add(worker)
            session.commit()
            session.refresh(worker)
            return worker

    def update(self, worker: Worker) -> Optional[Worker]:
        with self.session as session:
            existing_worker = session.get(Worker, worker.id)
            if existing_worker is None:
                return None
            worker_data = worker.model_dump(exclude_unset=True)
            for key, value in worker_data.items():
                setattr(existing_worker, key, value)
            session.add(existing_worker)
            session.commit()
            session.refresh(existing_worker)
            return existing_worker

    def delete(self, worker_id: int) -> bool:
        with self.session as session:
            worker = session.get(Worker, worker_id)
            if worker is None:
                return False
            session.delete(worker)
            session.commit()
            return True
