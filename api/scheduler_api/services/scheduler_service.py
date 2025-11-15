from scheduler_api.celery import app
from scheduler_api.models.schedule_dtos import (
    GenerateScheduleInput,
    GenerateScheduleResult,
)


class SchedulerService:
    @staticmethod
    def async_generate_schedule(input_dto: GenerateScheduleInput):
        # send_task uses the fully-qualified name of the task
        task = app.send_task(
            "scheduler_api.tasks.scheduler_tasks.generate_schedule_task",
            args=[input_dto.dict()],
        )
        return task.id

    @staticmethod
    def get_schedule_result(task_id: str) -> GenerateScheduleResult | None:
        from celery.result import AsyncResult

        result = AsyncResult(task_id, app=app)
        if result.ready():
            return GenerateScheduleResult(**result.result)
        return None
