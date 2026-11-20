from __future__ import annotations

from collections.abc import Sequence

from scheduler_api.engine.exceptions import MissingScorerOutputError
from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.scores import ScoringPolicy


def total_score(individual: Individual, policy: ScoringPolicy) -> float:
    total = 0.0
    for weight in policy.weights:
        if weight.component_id not in individual.scores:
            raise MissingScorerOutputError(individual.id, weight.component_id)
        total += weight.weight * individual.scores[weight.component_id]
    return total


def ranking_key(individual: Individual, policy: ScoringPolicy) -> tuple[int, float]:
    # 0 = feasible, 1 = infeasible; lower keys sort first.
    return (0 if individual.feasible else 1, -total_score(individual, policy))


def rank_individuals(
    individuals: Sequence[Individual], policy: ScoringPolicy
) -> tuple[Individual, ...]:
    return tuple(
        sorted(individuals, key=lambda individual: ranking_key(individual, policy))
    )
