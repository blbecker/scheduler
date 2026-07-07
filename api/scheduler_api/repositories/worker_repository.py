from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from scheduler_api.db.models.core.worker import WorkerModel


class WorkerRepository:
    """
    Repository for worker data access.
    
    Repositories are responsible for data access only.
    They never commit or rollback transactions - services own transaction boundaries.
    """
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[WorkerModel]:
        """Get all workers."""
        statement = select(WorkerModel)
        result = self.session.exec(statement)
        return list(result.all())

    def get_by_id(self, worker_id: UUID) -> Optional[WorkerModel]:
        """Get worker by ID."""
        return self.session.get(WorkerModel, worker_id)

    def add(self, worker: WorkerModel) -> WorkerModel:
        """
        Add a worker to the session.
        
        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.add(worker)
        # No commit - service owns transaction
        return worker

    def delete(self, worker: WorkerModel) -> None:
        """
        Delete a worker from the session.
        
        Note: Does not commit - service owns transaction boundaries.
        """
        self.session.delete(worker)
        # No commit - service owns transaction
