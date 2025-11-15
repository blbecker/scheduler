from __future__ import annotations
from typing import List, Callable
from pydantic import BaseModel

from .population import (
    generate_initial_population,
    Population,
)
from .selection import select_survivors
from .mutation import mutate_population
from .scoring import ScoreResult

from scheduler_api.schemas import ScheduleTemplateDTO
from scheduler_api.models import ScheduleTemplate


class GAConfig(BaseModel):
    population_size: int = 50
    generations: int = 50
    mutation_rate: float = 0.05
    elitism: int = 2


async def run_genetic_algorithm(
    schedule_template: ScheduleTemplate,
    scorers: List[Callable[[ScheduleTemplate], ScoreResult]],
    config: GAConfig,
) -> ScheduleTemplate:
    """
    Top-level GA entrypoint. Currently a single task, later decomposable.
    """

    population: Population = generate_initial_population(
        schedule_template=schedule_template,
        size=config.population_size,
    )

    for _ in range(config.generations):

        # Score
        population.score(scorers)

        # Selection
        population = select_survivors(
            population=population,
            elitism=config.elitism,
        )

        # Mutation
        population = mutate_population(
            population=population,
            mutation_rate=config.mutation_rate,
        )

    # Final scoring
    population.score(scorers)

    # Best schedule
    return population.best().schedule
