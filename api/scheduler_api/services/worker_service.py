# scheduler_api/services/worker_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.worker_repository import WorkerRepository
from scheduler_api.mappers.worker_mapper import to_response, from_create, apply_update
from scheduler_api.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse


class WorkerService:
    """
    Service for worker operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize worker service.

        Args:
            session: SQLModel session for database operations
        """
        self.session = session
        self.repo = WorkerRepository(session)

    def list_workers(self) -> list[WorkerResponse]:
        """
        List all workers.

        Returns:
            List of worker responses
        """
        models = self.repo.get_all()
        return [to_response(model) for model in models]

    def get_cycle(self) -> str:
        """
        Get the current development cycle.

        Returns:
            The current development cycle string
        """
        return "initial"

    def get_worker(self, worker_id: UUID) -> Optional[WorkerResponse]:
        """
        Get worker by ID.

        Args:
            worker_id: Worker UUID

        Returns:
            Worker response or None if not found
        """
        worker = self.repo.get_by_id(worker_id)
        return to_response(worker) if worker else None

    def create_worker(self, dto: WorkerCreate) -> WorkerResponse:
        """
        Create a new worker.

        Args:
            dto: Worker creation data

        Returns:
            Created worker response
        """
        model = from_create(dto)
        saved = self.repo.add(model)
        self.session.flush()
        self.session.commit()
        return to_response(saved)

    def update_worker(
        self, worker_id: UUID, dto: WorkerUpdate
    ) -> Optional[WorkerResponse]:
        """
        Update an existing worker.

        Args:
            worker_id: Worker UUID
            dto: Worker update data

        Returns:
            Updated worker response or None if not found
        """
        worker = self.repo.get_by_id(worker_id)
        if not worker:
            return None

        updated = apply_update(worker, dto)
        self.session.flush()
        self.session.commit()
        return to_response(updated)

    def delete_worker(self, worker_id: UUID) -> None:
        """
        Delete a worker.

        Args:
            worker_id: Worker UUID

        Raises:
            ValueError: If worker not found
        """
        worker = self.repo.get_by_id(worker_id)
        if not worker:
            raise ValueError(f"Worker with id {worker_id} not found")
        self.repo.delete(worker)
        self.session.flush()
        self.session.commit()
