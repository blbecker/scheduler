from __future__ import annotations
from typing import List

# import random
from pydantic import BaseModel

from .scoring import ScoreResult
from scheduler_api.models import ScheduleTemplate


class Individual(BaseModel):
    schedule: ScheduleTemplate
    score: float = 0.0
    hard_fail: bool = False
    messages: List[str] = []


class Population(BaseModel):
    individuals: List[Individual]

    def score(self, scorers):
        for ind in self.individuals:
            failures = []
            total = 0.0

            for scorer in scorers:
                result: ScoreResult = scorer(ind.schedule)

                if not result.ok:
                    failures.append(result.message)
                total += result.score

            ind.score = total
            ind.messages = failures
            ind.hard_fail = len(failures) > 0

    def best(self) -> Individual:
        sorted_inds = sorted(
            self.individuals,
            key=lambda i: (i.hard_fail, -i.score),
        )
        return sorted_inds[0]


def clone_schedule(schedule: ScheduleTemplate) -> ScheduleTemplate:
    """Deep-clone a persisted model into a new object tree."""
    data = schedule.model_dump()
    return ScheduleTemplate(**data)


def generate_initial_population(
    schedule_template: ScheduleTemplate,
    size: int,
) -> Population:
    individuals = []

    for _ in range(size):
        new_sched = clone_schedule(schedule_template)
        # later: random assignments of workers etc.
        individuals.append(Individual(schedule=new_sched))

    return Population(individuals=individuals)
