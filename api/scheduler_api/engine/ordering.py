"""The canonical candidate ordering.

One ordering, used by selection, culling, best-candidate tracking, and candidate
ranking. It must be total and deterministic: early populations are full of exact
ties, and an unstable tie-break makes a seeded run irreproducible.
"""

from __future__ import annotations

from datetime import datetime

from scheduler_api.engine.models.genome import Individual

SortKey = tuple[int, float, tuple[tuple[str, datetime, datetime, str], ...], str]


def individual_sort_key(individual: Individual) -> SortKey:
    """Ascending key that puts the best individual first."""
    feasible_rank = 0 if individual.feasible else 1
    fitness = individual.fitness if individual.fitness is not None else -1.0
    return (feasible_rank, -fitness, individual.structural_key, str(individual.id))


def rank_individuals(individuals: tuple[Individual, ...]) -> tuple[Individual, ...]:
    """Sort candidates best first."""
    return tuple(sorted(individuals, key=individual_sort_key))


def best_of(individuals: tuple[Individual, ...]) -> Individual | None:
    """The best individual in a collection, or ``None`` when empty."""
    if not individuals:
        return None
    return min(individuals, key=individual_sort_key)


def better_of(left: Individual | None, right: Individual | None) -> Individual | None:
    """Whichever of two candidates ranks better."""
    if left is None:
        return right
    if right is None:
        return left
    return min(left, right, key=individual_sort_key)
