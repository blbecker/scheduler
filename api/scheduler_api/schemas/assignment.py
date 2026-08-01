"""Shift assignment schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from scheduler_api.domain.schedule import ShiftAssignmentStatus


class ShiftAssignmentBase(BaseModel):
    """Base schema for shift assignment data."""

    shift_id: UUID = Field(..., description="ID of the shift being assigned")
    worker_id: Optional[UUID] = Field(
        default=None,
        description="ID of the worker assigned to the shift (null for unassigned)",
    )
    status: ShiftAssignmentStatus = Field(
        default=ShiftAssignmentStatus.ASSIGNED,
        description="Current status of the assignment",
    )


class ShiftAssignmentCreate(ShiftAssignmentBase):
    """Schema for creating a new shift assignment."""

    schedule_id: UUID = Field(
        ..., description="ID of the schedule this assignment belongs to"
    )


class ShiftAssignmentUpdate(BaseModel):
    """Schema for updating an existing shift assignment."""

    worker_id: Optional[UUID] = Field(
        None, description="New worker ID for the assignment"
    )
    status: Optional[ShiftAssignmentStatus] = Field(
        None, description="New status of the assignment"
    )


class ShiftAssignmentResponse(ShiftAssignmentBase):
    """Schema for shift assignment response."""

    id: UUID = Field(..., description="Unique identifier of the assignment")
    schedule_id: UUID = Field(
        ..., description="ID of the schedule this assignment belongs to"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when assignment was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when assignment was last updated"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ShiftAssignmentListResponse(BaseModel):
    """Schema for list of shift assignments response."""

    assignments: list[ShiftAssignmentResponse] = Field(
        default_factory=list, description="List of shift assignments"
    )
    total: int = Field(..., description="Total number of assignments")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
