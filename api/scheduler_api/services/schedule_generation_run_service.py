# scheduler_api/services/schedule_generation_run_service.py
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from scheduler_api.repositories.schedule_generation_run_repository import (
    ScheduleGenerationRunRepository,
)
from scheduler_api.mappers.schedule_generation_run_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.schedule_generation_run import (
    ScheduleGenerationRun,
    ScheduleGenerationRunResponse,
    ScheduleGenerationRunUpdate,
)
from scheduler_api.uow.unit_of_work import UnitOfWork


class ScheduleGenerationRunService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def list_schedule_generation_runs(self) -> List[ScheduleGenerationRunResponse]:
        repo = ScheduleGenerationRunRepository(self.uow.session)
        models = repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule_generation_run(self, id: UUID) -> ScheduleGenerationRunResponse:
        repo = ScheduleGenerationRunRepository(self.uow.session)
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule generation run with id {id} not found",
            )
        return to_response(model)

    def create_schedule_generation_run(
        self, dto: ScheduleGenerationRun
    ) -> ScheduleGenerationRunResponse:
        repo = ScheduleGenerationRunRepository(self.uow.session)
        model = from_create(dto)
        saved_model = repo.add(model)
        self.uow.flush()  # Generate IDs if needed
        return to_response(saved_model)

    def update_schedule_generation_run(
        self, id: UUID, dto: ScheduleGenerationRunUpdate
    ) -> ScheduleGenerationRunResponse:
        repo = ScheduleGenerationRunRepository(self.uow.session)
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule generation run with id {id} not found",
            )
        updated_model = apply_update(model, dto)
        repo.add(updated_model)
        self.uow.flush()  # Ensure updates are persisted
        return to_response(updated_model)

    def delete_schedule_generation_run(self, id: UUID) -> None:
        repo = ScheduleGenerationRunRepository(self.uow.session)
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule generation run with id {id} not found",
            )
        repo.delete(model)
        # No flush needed for delete operations
