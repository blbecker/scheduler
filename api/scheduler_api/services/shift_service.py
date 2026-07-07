# scheduler_api/services/shift_service.py
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from scheduler_api.repositories.shift_repository import ShiftRepository
from scheduler_api.mappers.shift_mapper import to_response, from_create, apply_update
from scheduler_api.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse


class ShiftService:
    """
    Service for shift operations.

    Services own transaction boundaries.
    Repositories are data access only and never commit/rollback transactions.
    """

    def __init__(self, session: Session):
        """
        Initialize shift service.

        Args:
            session: SQLModel session for database operations
        """
        self.session = session
        self.repo = ShiftRepository(session)

    def list_shifts(self) -> list[ShiftResponse]:
        """
        List all shifts.

        Returns:
            List of shift responses
        """
        models = self.repo.get_all()
        return [to_response(s) for s in models]

    def get_shift(self, shift_id: UUID) -> Optional[ShiftResponse]:
        """
        Get shift by ID.

        Args:
            shift_id: Shift ID

        Returns:
            Shift response if found, None otherwise
        """
        shift = self.repo.get_by_id(shift_id)
        return to_response(shift) if shift else None

    def create_shift(self, dto: ShiftCreate) -> ShiftResponse:
        """
        Create a new shift.

        Args:
            dto: Shift creation data

        Returns:
            Created shift response
        """
        model = from_create(dto)
        saved = self.repo.add(model)
        self.session.flush()
        self.session.commit()
        return to_response(saved)

    def update_shift(self, shift_id: UUID, dto: ShiftUpdate) -> Optional[ShiftResponse]:
        """
        Update an existing shift.

        Args:
            shift_id: Shift ID to update
            dto: Shift update data

        Returns:
            Updated shift response if found, None otherwise
        """
        existing = self.repo.get_by_id(shift_id)
        if not existing:
            return None

        updated = apply_update(existing, dto)
        saved = self.repo.add(updated)
        self.session.flush()
        self.session.commit()
        return to_response(saved)

    def delete_shift(self, shift_id: UUID) -> None:
        """
        Delete a shift.

        Args:
            shift_id: Shift ID to delete

        Raises:
            ValueError: If shift not found
        """
        shift = self.repo.get_by_id(shift_id)
        if not shift:
            raise ValueError(f"Shift with id {shift_id} not found")
        self.repo.delete(shift)
        self.session.flush()
        self.session.commit()
