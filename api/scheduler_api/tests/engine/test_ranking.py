from __future__ import annotations

import pytest

from scheduler_api.engine.exceptions import MissingScorerOutputError
from scheduler_api.engine.models.scores import Violation, ViolationCode
from scheduler_api.engine.ranking import (
    rank_individuals,
    ranking_key,
    total_score,
)
from scheduler_api.tests.engine.factories import (
    make_individual,
    make_policy,
)


def test_total_score_is_weighted_sum():
    policy = make_policy(("coverage", 1.0), ("shift_length", 0.5))
    individual = make_individual(scores={"coverage": 0.8, "shift_length": 0.4})

    assert total_score(individual, policy) == pytest.approx(1.0)


def test_total_score_requires_every_weighted_score():
    policy = make_policy(("coverage", 1.0))
    individual = make_individual(scores={})

    with pytest.raises(MissingScorerOutputError):
        total_score(individual, policy)


def test_feasible_ranks_before_infeasible():
    policy = make_policy(("coverage", 1.0))
    violation = Violation(
        code=ViolationCode.UNKNOWN_WORKER,
        message="missing",
    )
    feasible = make_individual(individual_id=1, scores={"coverage": 0.1})
    infeasible = make_individual(individual_id=2, scores={"coverage": 1.0})
    infeasible = infeasible.model_copy(update={"violations": (violation,)})

    ranked = rank_individuals((infeasible, feasible), policy)

    assert [individual.id for individual in ranked] == [
        feasible.id,
        infeasible.id,
    ]
    assert ranking_key(feasible, policy) < ranking_key(infeasible, policy)


def test_ranking_ties_preserve_input_order():
    policy = make_policy(("coverage", 1.0))
    first = make_individual(individual_id=1, scores={"coverage": 0.5})
    second = make_individual(individual_id=2, scores={"coverage": 0.5})

    ranked = rank_individuals((second, first), policy)

    assert ranked == (second, first)
