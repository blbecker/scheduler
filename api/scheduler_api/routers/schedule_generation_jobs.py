from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID

from scheduler_api.schemas.schedule_generation_job import (
    ScheduleGenerationJobCreateDTO,
    ScheduleGenerationJobDTO,
)

router = APIRouter(
    prefix="/schedule-generation-jobs",
    tags=["schedule-generation-jobs"],
)


@router.post("", response_model=ScheduleGenerationJobDTO, status_code=201)
async def create_schedule_generation_job(
    payload: ScheduleGenerationJobCreateDTO,
) -> ScheduleGenerationJobDTO:
    # TODO:
    # - validate schedule_template_id exists
    # - create job record in DB
    # - dispatch Celery task
    raise NotImplementedError


@router.get("", response_model=List[ScheduleGenerationJobDTO])
async def list_schedule_generation_jobs() -> List[ScheduleGenerationJobDTO]:
    # TODO: list all jobs, possibly with filters
    raise NotImplementedError


@router.get("/{job_id}", response_model=ScheduleGenerationJobDTO)
async def get_schedule_generation_job(job_id: UUID) -> ScheduleGenerationJobDTO:
    # TODO:
    # - retrieve job
    # - merge persisted DB state + Celery state if needed
    raise NotImplementedError
