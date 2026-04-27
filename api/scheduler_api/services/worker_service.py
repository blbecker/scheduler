# scheduler_api/services/worker_service.py
from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.mappers.worker_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse


class WorkerService:
    def __init__(self, repo: WorkerRepository):
        self.repo = repo

    def list_workers(self) -> list[WorkerResponse]:
        return [to_response(s) for s in self.repo.get_all()]

    def get_worker(self, worker_id: int) -> WorkerResponse | None:
        worker = self.repo.get_by_id(worker_id)
        return to_response(worker) if worker else None

    def create_worker(self, dto: WorkerCreate) -> WorkerResponse:
        model = from_create(dto)
        saved = self.repo.add(model)
        return to_response(saved)

    def update_worker(self, worker_id: int, dto: WorkerUpdate) -> WorkerResponse | None:
        existing = self.repo.get_by_id(worker_id)
        if not existing:
            return None

        updated = apply_update(existing, dto)
        saved = self.repo.add(updated)
        return to_response(saved)

    def delete_worker(self, worker_id: int) -> bool:
        return self.repo.delete(worker_id)
