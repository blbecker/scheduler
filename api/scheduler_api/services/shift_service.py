from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status

from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.mappers.shift_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.shift import Shift, ShiftUpdate, ShiftResponse
from scheduler_api.uow.unit_of_work import UnitOfWork


class ShiftService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def list_shifts(self) -> list[ShiftResponse]:
        repo = ShiftRepository(self.uow.session)
        return [to_response(s) for s in repo.get_all()]

    def get_shift(self, shift_id: UUID) -> Optional[ShiftResponse]:
        repo = ShiftRepository(self.uow.session)
        shift = repo.get_by_id(shift_id)
        return to_response(shift) if shift else None

    def create_shift(self, dto: Shift) -> ShiftResponse:
        repo = ShiftRepository(self.uow.session)
        model = from_create(dto)
        saved = repo.add(model)
        self.uow.flush()  # Generate IDs if needed
        return to_response(saved)

    def update_shift(self, shift_id: UUID, dto: ShiftUpdate) -> Optional[ShiftResponse]:
        repo = ShiftRepository(self.uow.session)
        existing = repo.get_by_id(shift_id)
        if not existing:
            return None

        updated = apply_update(existing, dto)
        saved = repo.add(updated)
        self.uow.flush()  # Ensure updates are persisted
        return to_response(saved)

    def delete_shift(self, shift_id: UUID) -> None:
        repo = ShiftRepository(self.uow.session)
        shift = repo.get_by_id(shift_id)
        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shift with id {shift_id} not found",
            )
        repo.delete(shift)
        # No flush needed for delete operations
