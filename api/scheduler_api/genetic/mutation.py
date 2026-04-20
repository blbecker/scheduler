from __future__ import annotations
import random
from typing import List
from .population import Population, clone_schedule, Individual


def mutate_population(
    population: Population,
    mutation_rate: float,
) -> Population:
    mutated: List[Individual] = []

    for ind in population.individuals:
        schedule_copy = clone_schedule(ind.schedule)

        if random.random() < mutation_rate:
            apply_mutation(schedule_copy)

        mutated.append(Individual(schedule=schedule_copy))

    return Population(individuals=mutated)


def apply_mutation(schedule):
    """
    Placeholder for real mutation logic.
    Later: swap workers, adjust shift assignments, add/remove breaks, etc.
    """
    pass
