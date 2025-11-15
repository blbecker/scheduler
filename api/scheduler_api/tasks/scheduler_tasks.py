import time
from celery import shared_task
from scheduler_api.models.schedule_dtos import (
    GenerateScheduleInput,
    GenerateScheduleResult,
)


@shared_task
def generate_schedule_task(input_dict: dict) -> dict:
    """
    input_dict is a dict representation of GenerateScheduleInput
    """
    input_data = GenerateScheduleInput(**input_dict)
    total = input_data.total_seconds_to_wait
    for i in range(1, total + 1):
        time.sleep(1)
        print(f"Worker: generating schedule ({i}/{total})")

    return GenerateScheduleResult(status="success", seconds_waited=total).dict()
