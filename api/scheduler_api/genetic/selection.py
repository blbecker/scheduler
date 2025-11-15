from __future__ import annotations
from typing import List
import random

from .population import Population, Individual


def select_survivors(
    population: Population,
    elitism: int,
) -> Population:

    # Sort by fails first, then by score descending
    sorted_inds = sorted(
        population.individuals,
        key=lambda i: (i.hard_fail, -i.score),
    )

    elites = sorted_inds[:elitism]

    # Tournament selection for the remaining slots
    remaining = len(sorted_inds) - elitism
    selected = []

    for _ in range(remaining):
        a, b = random.sample(sorted_inds, 2)
        selected.append(a if a.score > b.score else b)

    return Population(individuals=elites + selected)
