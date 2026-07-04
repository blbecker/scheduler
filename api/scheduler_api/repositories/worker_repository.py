from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.core.worker import WorkerModel


class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[WorkerModel]:
        statement = select(WorkerModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, worker_id: UUID) -> Optional[WorkerModel]:
        return self.session.get(WorkerModel, worker_id)

    def add(self, worker: WorkerModel) -> WorkerModel:
        self.session.add(worker)
        return worker

    def delete(self, worker: WorkerModel) -> None:
        self.session.delete(worker)
