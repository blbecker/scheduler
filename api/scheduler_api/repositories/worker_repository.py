from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.core.worker import Worker


class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Worker]:
        statement = select(Worker)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, worker_id: UUID) -> Optional[Worker]:
        return self.session.get(Worker, worker_id)

    def add(self, worker: Worker) -> Worker:
        self.session.add(worker)
        return worker

    def delete(self, worker: Worker) -> None:
        self.session.delete(worker)
