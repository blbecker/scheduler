from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.mappers.shift_mapper import (
    to_response,
    from_create,
    apply_update,
)
from scheduler_api.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse


class ShiftService:
    def __init__(self, repo: ShiftRepository):
        self.repo = repo

    def list_shifts(self) -> list[ShiftResponse]:
        return [to_response(s) for s in self.repo.get_all()]

    def get_shift(self, shift_id: int) -> ShiftResponse | None:
        shift = self.repo.get_by_id(shift_id)
        return to_response(shift) if shift else None

    def create_shift(self, dto: ShiftCreate) -> ShiftResponse:
        model = from_create(dto)
        saved = self.repo.add(model)
        return to_response(saved)

    def update_shift(self, shift_id: int, dto: ShiftUpdate) -> ShiftResponse | None:
        existing = self.repo.get_by_id(shift_id)
        if not existing:
            return None

        updated = apply_update(existing, dto)
        saved = self.repo.add(updated)  # or session merge in repo
        return to_response(saved)
