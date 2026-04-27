from scheduler_api.db.models import Worker
from sqlmodel import Session


class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Worker]:
        return self.session.query(Worker).all()

    def get_by_id(self, worker_id: int) -> Worker | None:
        return self.session.get(Worker, worker_id)

    def add(self, worker: Worker) -> Worker:
        self.session.add(worker)
        self.session.commit()
        self.session.refresh(worker)
        return worker

    def delete(self, worker_id: int) -> bool:
        obj = self.session.get(Worker, worker_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True
