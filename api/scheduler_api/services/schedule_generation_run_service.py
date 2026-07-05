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


class ScheduleGenerationRunService:
    def __init__(self, repo: ScheduleGenerationRunRepository):
        self.repo = repo

    def list_schedule_generation_runs(self) -> List[ScheduleGenerationRunResponse]:
        repo = self.repo
        models = repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule_generation_run(self, id: UUID) -> ScheduleGenerationRunResponse:
        repo = self.repo
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
        repo = self.repo
        model = from_create(dto)
        saved_model = repo.add(model)
        return to_response(saved_model)

    def update_schedule_generation_run(
        self, id: UUID, dto: ScheduleGenerationRunUpdate
    ) -> ScheduleGenerationRunResponse:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule generation run with id {id} not found",
            )
        updated_model = apply_update(model, dto)
        repo.add(updated_model)
        return to_response(updated_model)

    def delete_schedule_generation_run(self, id: UUID) -> None:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule generation run with id {id} not found",
            )
        repo.delete(model)
        # No flush needed for delete operations
