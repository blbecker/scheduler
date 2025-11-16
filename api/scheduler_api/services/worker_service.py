# scheduler_api/services/worker_service.py
from typing import List, Optional
from scheduler_api.models import Worker
from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.schemas.worker import WorkerCreate, WorkerUpdate
from uuid import UUID


class WorkerService:
    def __init__(self, repo: WorkerRepository):
        self.repo = repo

    def list_workers(self) -> List[Worker]:
        return self.repo.get_all()

    def get_worker(self, worker_id: UUID) -> Optional[Worker]:
        return self.repo.get_by_id(worker_id)

    def create_worker(self, worker: WorkerCreate) -> Worker:
        return self.repo.add(worker)

    def update_worker(self, worker: WorkerUpdate) -> Optional[Worker]:
        return self.repo.update(worker)

    def delete_worker(self, worker_id: UUID) -> bool:
        return self.repo.delete(worker_id)
