from __future__ import annotations

from scheduler_api.engine.components.scorers.overlap import (
    WorkerOverlapScorer,
)
from scheduler_api.engine.models.component_io import ScoreInput
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.scores import ViolationCode
from scheduler_api.tests.engine.factories import (
    make_assignment,
    make_individual,
    make_job,
    make_problem,
)


def make_input(problem, *individuals):
    return ScoreInput(
        category="scorer",
        problem=problem,
        population=Population(individuals=tuple(individuals)),
    )


def test_double_booking_is_a_violation():
    problem = make_problem(jobs=(make_job(11), make_job(12)))
    individual = make_individual(
        assignments=(
            make_assignment(job_id=11, slot_index=1),
            make_assignment(job_id=12, slot_index=1),
        )
    )

    result = WorkerOverlapScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 0.5
    assert result.updates[0].violations[0].code is (ViolationCode.WORKER_DOUBLE_BOOKED)


def test_disjoint_assignments_score_one():
    problem = make_problem()
    individual = make_individual(
        assignments=(
            make_assignment(slot_index=0),
            make_assignment(slot_index=1),
        )
    )

    result = WorkerOverlapScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 1.0
    assert result.updates[0].violations == ()


def test_empty_schedule_scores_one():
    result = WorkerOverlapScorer().score(make_input(make_problem(), make_individual()))

    assert result.updates[0].score == 1.0


def test_scorer_does_not_mutate_input():
    individual = make_individual(
        assignments=(
            make_assignment(job_id=11),
            make_assignment(job_id=12),
        )
    )
    score_input = make_input(
        make_problem(jobs=(make_job(11), make_job(12))), individual
    )
    before = score_input.model_dump(mode="json")

    WorkerOverlapScorer().score(score_input)

    assert score_input.model_dump(mode="json") == before
