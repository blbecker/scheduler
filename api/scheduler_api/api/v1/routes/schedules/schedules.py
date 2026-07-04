# scheduler_api/routers/schedules.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.schemas.schedule_crud import (
    Schedule,
    ScheduleUpdate,
    ScheduleResponse,
)
from scheduler_api.uow.unit_of_work import UnitOfWork

from ..deps import get_unit_of_work_provider

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("/", response_model=list[ScheduleResponse], operation_id="list_schedules")
def list_schedules(uow: UnitOfWork = Depends(get_unit_of_work_provider())):
    service = ScheduleService(uow)
    return service.list_schedules()


@router.get(
    "/{schedule_id}", response_model=ScheduleResponse, operation_id="get_schedule"
)
def get_schedule(
    schedule_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleService(uow)
    try:
        return service.get_schedule(schedule_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule not found")


@router.post(
    "/",
    response_model=ScheduleResponse,
    operation_id="create_schedule",
    status_code=201,
)
def create_schedule(
    schedule: Schedule,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleService(uow)
    return service.create_schedule(schedule)


@router.put(
    "/{schedule_id}", response_model=ScheduleResponse, operation_id="update_schedule"
)
def update_schedule(
    schedule_id: UUID,
    schedule: ScheduleUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleService(uow)
    try:
        return service.update_schedule(schedule_id, schedule)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule not found")


@router.delete("/{schedule_id}", operation_id="delete_schedule", status_code=204)
def delete_schedule(
    schedule_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleService(uow)
    try:
        service.delete_schedule(schedule_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return None
