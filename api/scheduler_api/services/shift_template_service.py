# scheduler_api/services/shift_template_service.py
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from scheduler_api.repositories.shift_template_repository import ShiftTemplateRepository
from scheduler_api.mappers.shift_template_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.shift_template import (
    ShiftTemplate,
    ShiftTemplateResponse,
    ShiftTemplateUpdate,
)


class ShiftTemplateService:
    def __init__(self, repo: ShiftTemplateRepository):
        self.repo = repo

    def list_shift_templates(self) -> List[ShiftTemplateResponse]:
        repo = self.repo
        models = repo.get_all()
        return [to_response(model) for model in models]

    def get_shift_template(self, id: UUID) -> ShiftTemplateResponse:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shift template with id {id} not found",
            )
        return to_response(model)

    def create_shift_template(self, dto: ShiftTemplate) -> ShiftTemplateResponse:
        repo = self.repo
        model = from_create(dto)
        saved_model = repo.add(model)
        return to_response(saved_model)

    def update_shift_template(
        self, id: UUID, dto: ShiftTemplateUpdate
    ) -> ShiftTemplateResponse:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shift template with id {id} not found",
            )
        updated_model = apply_update(model, dto)
        repo.add(updated_model)
        return to_response(updated_model)

    def delete_shift_template(self, id: UUID) -> None:
        repo = self.repo
        model = repo.get_by_id(id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shift template with id {id} not found",
            )
        repo.delete(model)
        # No flush needed for delete operations
