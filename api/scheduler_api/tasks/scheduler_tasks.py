from celery import shared_task
from ..genetic.ga import run_ga
from ..schemas.dtos import ScheduleTemplateDTO, WorkerDTO
from ..scoring.base import SkillMatchScorer


@shared_task
def generate_schedule(template_data: dict, workers_data: list[dict]) -> dict:
    template = ScheduleTemplateDTO(**template_data)
    workers = [WorkerDTO(**w) for w in workers_data]
    scorer = SkillMatchScorer()
    best_schedule = run_ga(template, workers, scorer)
    return best_schedule.dict()
