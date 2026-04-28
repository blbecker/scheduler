import time
import random
import logging
from celery import shared_task, chain
from scheduler_api.schemas.ga_dtos import (
    ScheduleLayoutDTO,
    PopulationDTO,
    ScheduleDTO,
)
from scheduler_api.mappers.ga_mapper import (
    schedule_layout_from_dto,
    population_from_dto,
    population_to_dto,
    schedule_to_dto,
)
from scheduler_api.genetic.ga_operations import (
    generate_initial_population,
    score_population,
    mutate_population,
    breed_population,
    cull_population,
    select_best_schedule,
)

logger = logging.getLogger(__name__)


def _log_task_start(task_name: str):
    logger.info(f"[{task_name}] start")


def _log_task_end(task_name: str):
    logger.info(f"[{task_name}] end")


def _simulate_work():
    time.sleep(random.uniform(0.1, 1.5))


@shared_task
def population_generate(layout_dto: dict) -> dict:
    _log_task_start("population_generate")
    
    layout = schedule_layout_from_dto(ScheduleLayoutDTO(**layout_dto))
    population = generate_initial_population(layout, size=100)
    population_dto = population_to_dto(population)
    
    _simulate_work()
    _log_task_end("population_generate")
    
    return population_dto.model_dump()


@shared_task
def score_population_task(population_dto: dict) -> dict:
    _log_task_start("score_population")
    
    population = population_from_dto(PopulationDTO(**population_dto))
    scored_population = score_population(population)
    result_dto = population_to_dto(scored_population)
    
    _simulate_work()
    _log_task_end("score_population")
    
    return result_dto.model_dump()


@shared_task
def mutate_and_breed(population_dto: dict) -> dict:
    _log_task_start("mutate_and_breed")
    
    population = population_from_dto(PopulationDTO(**population_dto))
    
    mutated_population = mutate_population(population, mutation_rate=0.1)
    bred_population = breed_population(mutated_population, crossover_rate=0.8)
    
    result_dto = population_to_dto(bred_population)
    
    _simulate_work()
    _log_task_end("mutate_and_breed")
    
    return result_dto.model_dump()


@shared_task
def cull_population_task(population_dto: dict) -> dict:
    _log_task_start("cull_population")
    
    population = population_from_dto(PopulationDTO(**population_dto))
    culled_population = cull_population(population, target_size=100)
    result_dto = population_to_dto(culled_population)
    
    _simulate_work()
    _log_task_end("cull_population")
    
    return result_dto.model_dump()


@shared_task
def select_best(population_dto: dict) -> dict:
    _log_task_start("select_best")
    
    population = population_from_dto(PopulationDTO(**population_dto))
    best_schedule = select_best_schedule(population)
    
    best_schedule_dto = schedule_to_dto(best_schedule)
    
    _simulate_work()
    _log_task_end("select_best")
    
    return {
        "best_schedule": best_schedule_dto.model_dump(),
        "fitness": best_schedule.fitness or 0.0
    }


@shared_task
def generate_schedule_from_layout(layout_dto: dict) -> dict:
    _log_task_start("generate_schedule_from_layout")
    
    pipeline = chain(
        population_generate.s(layout_dto),
        score_population_task.s(),
        mutate_and_breed.s(),
        cull_population_task.s(),
        select_best.s()
    )
    
    result = pipeline()
    
    _log_task_end("generate_schedule_from_layout")
    
    return result.get() if hasattr(result, 'get') else result