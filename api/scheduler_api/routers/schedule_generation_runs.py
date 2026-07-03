# scheduler_api/routers/schedule_generation_runs.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from scheduler_api.services.schedule_generation_run_service import (
    ScheduleGenerationRunService,
)
from scheduler_api.schemas.schedule_generation_run import (
    ScheduleGenerationRunCreate,
    ScheduleGenerationRunUpdate,
    ScheduleGenerationRunResponse,
)
from scheduler_api.uow.unit_of_work import UnitOfWork

from .deps import get_unit_of_work_provider

router = APIRouter(
    prefix="/schedule-generation-runs", tags=["schedule-generation-runs"]
)


@router.get("/", response_model=list[ScheduleGenerationRunResponse])
def list_schedule_generation_runs(
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleGenerationRunService(uow)
    return service.list_schedule_generation_runs()


@router.get("/{run_id}", response_model=ScheduleGenerationRunResponse)
def get_schedule_generation_run(
    run_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleGenerationRunService(uow)
    try:
        return service.get_schedule_generation_run(run_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule generation run not found")


@router.post("/", response_model=ScheduleGenerationRunResponse, status_code=201)
def create_schedule_generation_run(
    run: ScheduleGenerationRunCreate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleGenerationRunService(uow)
    return service.create_schedule_generation_run(run)


@router.put("/{run_id}", response_model=ScheduleGenerationRunResponse)
def update_schedule_generation_run(
    run_id: UUID,
    run: ScheduleGenerationRunUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleGenerationRunService(uow)
    try:
        return service.update_schedule_generation_run(run_id, run)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule generation run not found")


@router.delete("/{run_id}", status_code=204)
def delete_schedule_generation_run(
    run_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work_provider()),
):
    service = ScheduleGenerationRunService(uow)
    try:
        service.delete_schedule_generation_run(run_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Schedule generation run not found")
    return None
