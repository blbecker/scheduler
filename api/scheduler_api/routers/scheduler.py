from uuid import UUID

from fastapi import APIRouter
from scheduler_api.services.scheduler_service import SchedulerService
from scheduler_api.models.schedule_dtos import (
    GenerateScheduleInput,
    GenerateScheduleResult,
)

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("/generate")
def create_schedule(input_dto: GenerateScheduleInput):
    task_id = SchedulerService.async_generate_schedule(input_dto)
    return {"task_id": task_id}


@router.get("/{task_id}", response_model=GenerateScheduleResult)
def get_schedule_result(task_id: UUID):
    result = SchedulerService.get_schedule_result(str(task_id))
    if result:
        return result
    return GenerateScheduleResult(status="pending", seconds_waited=0)
