# scheduler_api/services/schedule_service.py
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from scheduler_api.repositories.schedule_repository import ScheduleRepository
from scheduler_api.mappers.schedule_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.schedule_crud import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)
from scheduler_api.uow.unit_of_work import UnitOfWork


class ScheduleService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def list_schedules(self) -> List[ScheduleResponse]:
        repo = ScheduleRepository(self.uow.session)
        models = repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule(self, id: UUID) -> ScheduleResponse:
        repo = ScheduleRepository(self.uow.session)
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule with id {id} not found",
            )
        return to_response(model)

    def create_schedule(self, dto: ScheduleCreate) -> ScheduleResponse:
        repo = ScheduleRepository(self.uow.session)
        model = from_create(dto)
        saved_model = repo.add(model)
        self.uow.flush()  # Generate IDs if needed
        return to_response(saved_model)

    def update_schedule(self, id: UUID, dto: ScheduleUpdate) -> ScheduleResponse:
        repo = ScheduleRepository(self.uow.session)
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule with id {id} not found",
            )
        updated_model = apply_update(model, dto)
        repo.add(updated_model)
        self.uow.flush()  # Ensure updates are persisted
        return to_response(updated_model)

    def delete_schedule(self, id: UUID) -> None:
        repo = ScheduleRepository(self.uow.session)
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule with id {id} not found",
            )
        repo.delete(model)
        # No flush needed for delete operations
