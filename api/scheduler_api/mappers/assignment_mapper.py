# scheduler_api/mappers/assignment_mapper.py
from uuid import UUID
from typing import TYPE_CHECKING

from scheduler_api.db.models.assignments.shift_assignment import ShiftAssignmentModel
from scheduler_api.schemas.assignment import (
    ShiftAssignmentCreate,
    ShiftAssignmentResponse,
    ShiftAssignmentUpdate,
)

if TYPE_CHECKING:
    from scheduler_api.domain.schedule import ShiftAssignment


def to_response(model: ShiftAssignmentModel) -> ShiftAssignmentResponse:
    return ShiftAssignmentResponse(
        id=model.id,
        schedule_id=model.schedule_id,
        shift_id=model.shift_id,
        worker_id=model.worker_id,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: ShiftAssignmentCreate) -> ShiftAssignmentModel:
    return ShiftAssignmentModel(**dto.model_dump())


def apply_update(
    model: ShiftAssignmentModel, dto: ShiftAssignmentUpdate
) -> ShiftAssignmentModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model


def to_domain(model: ShiftAssignmentModel) -> "ShiftAssignment":
    """Convert database model to domain model."""
    from scheduler_api.domain.schedule import ShiftAssignment

    return ShiftAssignment(
        worker_id=model.worker_id,
        shift_id=model.shift_id,
        status=model.status,
    )


def from_domain(
    assignment: "ShiftAssignment", schedule_id: UUID
) -> ShiftAssignmentModel:
    """Convert domain model to database model."""
    from scheduler_api.domain.schedule import ShiftAssignmentStatus

    return ShiftAssignmentModel(
        schedule_id=schedule_id,
        shift_id=assignment.shift_id,
        worker_id=assignment.worker_id,
        status=assignment.status,
    )
