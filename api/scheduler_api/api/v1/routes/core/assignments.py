"""Shift assignment API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from scheduler_api.services.shift_assignment_service import ShiftAssignmentService
from scheduler_api.schemas.assignment import (
    ShiftAssignmentCreate,
    ShiftAssignmentUpdate,
    ShiftAssignmentResponse,
    ShiftAssignmentListResponse,
)

from ..deps import get_shift_assignment_service

router = APIRouter(prefix="/shift-assignments", tags=["shift-assignments"])


@router.get(
    "/",
    response_model=ShiftAssignmentListResponse,
    operation_id="list_shift_assignments",
)
def list_shift_assignments(
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """List all shift assignments."""
    return service.list_assignments()


@router.get(
    "/schedule/{schedule_id}",
    response_model=ShiftAssignmentListResponse,
    operation_id="get_assignments_by_schedule",
)
def get_assignments_by_schedule(
    schedule_id: UUID,
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Get all shift assignments for a schedule."""
    return service.get_assignments_by_schedule(schedule_id)


@router.get(
    "/shift/{shift_id}",
    response_model=ShiftAssignmentResponse,
    operation_id="get_assignment_by_shift",
)
def get_assignment_by_shift(
    shift_id: UUID,
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Get shift assignment for a specific shift."""
    assignment = service.get_assignment_by_shift(shift_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Shift assignment not found")
    return assignment


@router.get(
    "/worker/{worker_id}",
    response_model=ShiftAssignmentListResponse,
    operation_id="get_assignments_by_worker",
)
def get_assignments_by_worker(
    worker_id: UUID,
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Get all shift assignments for a worker."""
    return service.get_assignments_by_worker(worker_id)


@router.get(
    "/{assignment_id}",
    response_model=ShiftAssignmentResponse,
    operation_id="get_shift_assignment",
)
def get_shift_assignment(
    assignment_id: UUID,
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Get a specific shift assignment."""
    assignment = service.get_assignment(assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Shift assignment not found")
    return assignment


@router.post(
    "/",
    response_model=ShiftAssignmentResponse,
    operation_id="create_shift_assignment",
    status_code=201,
)
def create_shift_assignment(
    assignment: ShiftAssignmentCreate,
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Create a new shift assignment."""
    try:
        return service.create_assignment(assignment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/bulk/{schedule_id}",
    response_model=ShiftAssignmentListResponse,
    operation_id="bulk_create_shift_assignments",
    status_code=201,
)
def bulk_create_shift_assignments(
    schedule_id: UUID,
    assignments: List[ShiftAssignmentCreate],
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Create multiple shift assignments for a schedule."""
    try:
        return service.bulk_create_assignments(schedule_id, assignments)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{assignment_id}",
    response_model=ShiftAssignmentResponse,
    operation_id="update_shift_assignment",
)
def update_shift_assignment(
    assignment_id: UUID,
    assignment: ShiftAssignmentUpdate,
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Update a shift assignment."""
    updated = service.update_assignment(assignment_id, assignment)
    if updated is None:
        raise HTTPException(status_code=404, detail="Shift assignment not found")
    return updated


@router.delete(
    "/{assignment_id}", operation_id="delete_shift_assignment", status_code=204
)
def delete_shift_assignment(
    assignment_id: UUID,
    service: ShiftAssignmentService = Depends(get_shift_assignment_service),
):
    """Delete a shift assignment."""
    try:
        deleted = service.delete_assignment(assignment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Shift assignment not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
