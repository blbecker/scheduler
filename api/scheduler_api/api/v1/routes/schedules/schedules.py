# scheduler_api/routers/schedules.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session

from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.repositories.schedule_repository import ScheduleRepository
from scheduler_api.schemas.schedule_crud import (
    Schedule,
    ScheduleUpdate,
    ScheduleResponse,
)

from ..deps import get_db_session

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("/", response_model=list[ScheduleResponse], operation_id="list_schedules")
def list_schedules(session: Session = Depends(get_db_session)):
    repo = ScheduleRepository(session)
    service = ScheduleService(repo)
    return service.list_schedules()


@router.get(
    "/{schedule_id}", response_model=ScheduleResponse, operation_id="get_schedule"
)
def get_schedule(
    schedule_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ScheduleRepository(session)
    service = ScheduleService(repo)
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
    session: Session = Depends(get_db_session),
):
    repo = ScheduleRepository(session)
    service = ScheduleService(repo)
    return service.create_schedule(schedule)


@router.put(
    "/{schedule_id}", response_model=ScheduleResponse, operation_id="update_schedule"
)
def update_schedule(
    schedule_id: UUID,
    schedule: ScheduleUpdate,
    session: Session = Depends(get_db_session),
):
    repo = ScheduleRepository(session)
    service = ScheduleService(repo)
    try:
        return service.update_schedule(schedule_id, schedule)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule not found")


@router.delete("/{schedule_id}", operation_id="delete_schedule", status_code=204)
def delete_schedule(
    schedule_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = ScheduleRepository(session)
    service = ScheduleService(repo)
    try:
        service.delete_schedule(schedule_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return None
