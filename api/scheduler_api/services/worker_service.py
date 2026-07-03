# scheduler_api/services/worker_service.py
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status

from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.mappers.worker_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse
from scheduler_api.uow.unit_of_work import UnitOfWork


class WorkerService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def list_workers(self) -> List[WorkerResponse]:
        repo = WorkerRepository(self.uow.session)
        models = repo.get_all()
        return [to_response(s) for s in models]

    def get_worker(self, worker_id: UUID) -> Optional[WorkerResponse]:
        repo = WorkerRepository(self.uow.session)
        worker = repo.get_by_id(worker_id)
        return to_response(worker) if worker else None

    def create_worker(self, dto: WorkerCreate) -> WorkerResponse:
        repo = WorkerRepository(self.uow.session)
        model = from_create(dto)
        saved = repo.add(model)
        self.uow.flush()  # Generate IDs if needed
        return to_response(saved)

    def update_worker(
        self, worker_id: UUID, dto: WorkerUpdate
    ) -> Optional[WorkerResponse]:
        repo = WorkerRepository(self.uow.session)
        existing = repo.get_by_id(worker_id)
        if not existing:
            return None

        updated = apply_update(existing, dto)
        saved = repo.add(updated)
        self.uow.flush()  # Ensure updates are persisted
        return to_response(saved)

    def delete_worker(self, worker_id: UUID) -> None:
        repo = WorkerRepository(self.uow.session)
        worker = repo.get_by_id(worker_id)
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Worker with id {worker_id} not found",
            )
        repo.delete(worker)
        # No flush needed for delete operations
