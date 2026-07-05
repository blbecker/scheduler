# scheduler_api/services/schedule_template_service.py
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from scheduler_api.repositories.schedule_template_repository import (
    ScheduleTemplateRepository,
)
from scheduler_api.mappers.schedule_template_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplate,
    ScheduleTemplateResponse,
    ScheduleTemplateUpdate,
)


class ScheduleTemplateService:
    def __init__(self, repo: ScheduleTemplateRepository):
        self.repo = repo

    def list_schedule_templates(self) -> List[ScheduleTemplateResponse]:
        repo = self.repo
        models = repo.get_all()
        return [to_response(model) for model in models]

    def get_schedule_template(self, id: UUID) -> ScheduleTemplateResponse:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule template with id {id} not found",
            )
        return to_response(model)

    def create_schedule_template(
        self, dto: ScheduleTemplate
    ) -> ScheduleTemplateResponse:
        repo = self.repo
        model = from_create(dto)
        saved_model = repo.add(model)
        return to_response(saved_model)

    def update_schedule_template(
        self, id: UUID, dto: ScheduleTemplateUpdate
    ) -> ScheduleTemplateResponse:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule template with id {id} not found",
            )
        updated_model = apply_update(model, dto)
        repo.add(updated_model)
        return to_response(updated_model)

    def delete_schedule_template(self, id: UUID) -> None:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule template with id {id} not found",
            )
        repo.delete(model)
        # No flush needed for delete operations
