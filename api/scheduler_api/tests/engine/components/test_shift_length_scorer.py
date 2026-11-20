from __future__ import annotations

import pytest

from scheduler_api.engine.components.scorers.shift_length import (
    ShiftLengthScorer,
)
from scheduler_api.engine.models.component_config import (
    ShiftLengthScorerConfig,
)
from scheduler_api.engine.models.component_io import ScoreInput
from scheduler_api.engine.models.population import Population
from scheduler_api.tests.engine.factories import (
    make_assignment,
    make_individual,
    make_job,
    make_problem,
    make_worker,
)


def make_input(problem, *individuals):
    return ScoreInput(
        category="scorer",
        problem=problem,
        population=Population(individuals=tuple(individuals)),
    )


def test_run_within_limits_scores_one():
    problem = make_problem(
        workers=(make_worker(1, (11,), (0, 1, 2, 3), minimum=2, maximum=4),)
    )
    individual = make_individual(
        assignments=tuple(make_assignment(slot_index=index) for index in range(3))
    )

    result = ShiftLengthScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 1.0
    assert result.updates[0].violations == ()


def test_run_shorter_than_minimum_is_penalized():
    problem = make_problem(workers=(make_worker(1, (11,), (0, 1, 2), minimum=3),))
    individual = make_individual(assignments=(make_assignment(slot_index=0),))

    result = ShiftLengthScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 1 - 2 / 3


def test_run_longer_than_maximum_is_penalized():
    problem = make_problem(workers=(make_worker(1, (11,), (0, 1, 2, 3), maximum=2),))
    individual = make_individual(
        assignments=tuple(make_assignment(slot_index=index) for index in range(4))
    )

    result = ShiftLengthScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 0.0


def test_gap_splits_runs():
    problem = make_problem(workers=(make_worker(1, (11,), (0, 1, 2, 3), minimum=2),))
    individual = make_individual(
        assignments=(
            make_assignment(slot_index=0),
            make_assignment(slot_index=1),
            make_assignment(slot_index=3),
        )
    )

    result = ShiftLengthScorer().score(make_input(problem, individual))

    assert result.updates[0].score == (1.0 + 0.5) / 2


def test_job_change_splits_runs():
    problem = make_problem(
        jobs=(make_job(11), make_job(12)),
        workers=(make_worker(1, (11, 12), (0, 1, 2, 3), minimum=3),),
    )
    individual = make_individual(
        assignments=(
            make_assignment(job_id=11, slot_index=0),
            make_assignment(job_id=11, slot_index=1),
            make_assignment(job_id=12, slot_index=2),
            make_assignment(job_id=12, slot_index=3),
        )
    )

    result = ShiftLengthScorer().score(make_input(problem, individual))

    assert result.updates[0].score == pytest.approx(2 / 3)


def test_no_runs_scores_one():
    result = ShiftLengthScorer().score(make_input(make_problem(), make_individual()))

    assert result.updates[0].score == 1.0


def test_weights_are_configurable():
    problem = make_problem(workers=(make_worker(1, (11,), (0, 1, 2), minimum=3),))
    individual = make_individual(assignments=(make_assignment(slot_index=0),))
    scorer = ShiftLengthScorer(ShiftLengthScorerConfig(under_minimum_weight=0.0))

    result = scorer.score(make_input(problem, individual))

    assert result.updates[0].score == 1.0


def test_scorer_does_not_mutate_input():
    score_input = make_input(
        make_problem(), make_individual(assignments=(make_assignment(),))
    )
    before = score_input.model_dump(mode="json")

    ShiftLengthScorer().score(score_input)

    assert score_input.model_dump(mode="json") == before
