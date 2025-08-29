# scheduler_api/services/worker_service.py
from typing import List, Optional
from scheduler_api.models import Worker
from scheduler_api.repositories.worker_repository import WorkerRepository
from sqlmodel import Session
from typing import List, Dict


class WorkerService:
    def __init__(self, repo: WorkerRepository):
        self.repo = repo

    def list_workers(self) -> List[Worker]:
        return self.repo.get_all()

    def get_worker(self, worker_id: int) -> Optional[Worker]:
        return self.repo.get_by_id(worker_id)

    def create_worker(self, name: str, birthdate, email: str = None) -> Worker:
        worker = Worker(name=name, birthdate=birthdate, email=email)
        return self.repo.add(worker)


class WorkerService:
    def __init__(self, session: Session):
        self.session = session

    def list_workers(self) -> List[Dict]:
        # TODO: Implement actual database query
        return [{"id": 1, "name": "Sample Worker"}]
