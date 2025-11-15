from fastapi import APIRouter, Response, status
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


@router.get("/{task_id}", response_model=GenerateScheduleResult, status_code=status.HTTP_200_OK)
def get_schedule_result(task_id: str, response: Response):
    result, task_status = SchedulerService.get_schedule_result(task_id)

    if task_status == "pending":
        response.status_code = status.HTTP_202_ACCEPTED
        return GenerateScheduleResult(status="pending", seconds_waited=0)

    # task_status == "completed"
    return result
