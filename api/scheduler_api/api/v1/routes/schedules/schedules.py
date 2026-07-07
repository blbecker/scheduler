# scheduler_api/routers/schedules.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.schemas.schedule_crud import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
)

from ..deps import get_schedule_service

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("/", response_model=list[ScheduleResponse], operation_id="list_schedules")
def list_schedules(service: ScheduleService = Depends(get_schedule_service)):
    return service.list_schedules()


@router.get(
    "/{schedule_id}", response_model=ScheduleResponse, operation_id="get_schedule"
)
def get_schedule(
    schedule_id: UUID, service: ScheduleService = Depends(get_schedule_service)
):
    schedule = service.get_schedule(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post(
    "/",
    response_model=ScheduleResponse,
    operation_id="create_schedule",
    status_code=201,
)
def create_schedule(
    schedule: ScheduleCreate, service: ScheduleService = Depends(get_schedule_service)
):
    return service.create_schedule(schedule)


@router.put(
    "/{schedule_id}", response_model=ScheduleResponse, operation_id="update_schedule"
)
def update_schedule(
    schedule_id: UUID,
    schedule: ScheduleUpdate,
    service: ScheduleService = Depends(get_schedule_service),
):
    updated = service.update_schedule(schedule_id, schedule)
    if updated is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated


@router.delete("/{schedule_id}", operation_id="delete_schedule", status_code=204)
def delete_schedule(
    schedule_id: UUID, service: ScheduleService = Depends(get_schedule_service)
):
    try:
        service.delete_schedule(schedule_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Schedule not found")
