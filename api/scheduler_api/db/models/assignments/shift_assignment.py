"""ShiftAssignment database model for one-to-one worker-shift assignments."""

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship

from scheduler_api.db.models.base import BaseModel
from scheduler_api.domain.schedule import ShiftAssignmentStatus

if TYPE_CHECKING:
    from scheduler_api.db.models.schedules.schedule import ScheduleModel
    from scheduler_api.db.models.schedules.shift import ShiftModel
    from scheduler_api.db.models.core.worker import WorkerModel


class ShiftAssignmentModel(BaseModel, table=True):
    """One-to-one assignment of worker to shift with status metadata."""

    __tablename__ = "shift_assignments"

    schedule_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("schedules.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    shift_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("shifts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,  # One-to-one: each shift can have only one assignment
            index=True,
        )
    )

    worker_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("workers.id", ondelete="CASCADE"),
            nullable=True,  # Allow null for unassigned shifts
            index=True,
        ),
    )

    status: ShiftAssignmentStatus = Field(
        sa_column=Column(
            SQLEnum(ShiftAssignmentStatus),
            nullable=False,
            default=ShiftAssignmentStatus.ASSIGNED,
        )
    )

    # Relationships
    schedule: "ScheduleModel" = Relationship(back_populates="shift_assignments")
    shift: "ShiftModel" = Relationship(back_populates="assignment")
    worker: "WorkerModel" = Relationship(back_populates="shift_assignments")
