# scheduler_api/mappers/schedule_mapper.py
from typing import List, TYPE_CHECKING
from uuid import UUID
from scheduler_api.db.models.schedules.schedule import ScheduleModel
from scheduler_api.schemas.schedule_crud import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
    ScheduleDetailResponse,
)
from scheduler_api.mappers.shift_mapper import to_response as shift_to_response
from scheduler_api.mappers.assignment_mapper import (
    to_response as assignment_to_response,
)

if TYPE_CHECKING:
    from scheduler_api.domain.schedule import Schedule, ShiftAssignment


def to_response(model: ScheduleModel) -> ScheduleResponse:
    return ScheduleResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_detail_response(model: ScheduleModel) -> ScheduleDetailResponse:
    """Convert schedule model to detailed response with relationships."""
    shifts = [shift_to_response(shift) for shift in getattr(model, "shifts", [])]
    shift_assignments = [
        assignment_to_response(assignment)
        for assignment in getattr(model, "shift_assignments", [])
    ]

    return ScheduleDetailResponse(
        id=model.id,
        schedule_template_id=model.schedule_template_id,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
        shifts=shifts,
        shift_assignments=shift_assignments,
    )


def from_create(dto: ScheduleCreate) -> ScheduleModel:
    return ScheduleModel(**dto.model_dump())


def apply_update(model: ScheduleModel, dto: ScheduleUpdate) -> ScheduleModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model


def to_domain(model: ScheduleModel) -> "Schedule":
    """Convert database model to domain model."""
    from scheduler_api.domain.schedule import (
        Schedule,
        ShiftAssignment,
        ShiftAssignmentStatus,
    )

    # Get shift assignments from model
    shift_assignments: List[ShiftAssignment] = []
    for assignment_model in getattr(model, "shift_assignments", []):
        assignment = ShiftAssignment(
            worker_id=assignment_model.worker_id,
            shift_id=assignment_model.shift_id,
            status=ShiftAssignmentStatus(assignment_model.status),
        )
        shift_assignments.append(assignment)

    return Schedule(
        id=model.id,
        name=model.name,
        shift_assignments=shift_assignments,
        created_at=model.created_at,
    )


def from_domain(schedule: "Schedule", schedule_template_id: UUID) -> ScheduleModel:
    """Convert domain model to database model."""
    from scheduler_api.db.models.assignments.shift_assignment import (
        ShiftAssignmentModel,
    )

    # Create schedule model
    schedule_model = ScheduleModel(
        id=schedule.id,
        schedule_template_id=schedule_template_id,
        name=schedule.name,
        created_at=schedule.created_at,
    )

    # Add shift assignments
    for assignment in schedule.shift_assignments:
        assignment_model = ShiftAssignmentModel(
            schedule_id=schedule.id,
            shift_id=assignment.shift_id,
            worker_id=assignment.worker_id,
            status=assignment.status.value,
        )
        schedule_model.shift_assignments.append(assignment_model)

    return schedule_model
