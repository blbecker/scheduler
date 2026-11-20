from __future__ import annotations

from scheduler_api.engine.components.scorers.coverage import CoverageScorer
from scheduler_api.engine.models.component_config import (
    CoverageScorerConfig,
)
from scheduler_api.engine.models.component_io import ScoreInput
from scheduler_api.engine.models.population import Population
from scheduler_api.tests.engine.factories import (
    make_assignment,
    make_demand,
    make_individual,
    make_job,
    make_problem,
    make_slots,
    make_worker,
)


def make_input(problem, *individuals):
    return ScoreInput(
        category="scorer",
        problem=problem,
        population=Population(individuals=tuple(individuals)),
    )


def test_fully_covered_schedule_scores_one():
    problem = make_problem()
    individual = make_individual(
        assignments=tuple(make_assignment(slot_index=index) for index in range(4))
    )

    result = CoverageScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 1.0
    assert result.updates[0].violations == ()


def test_understaffing_reduces_score():
    problem = make_problem(staffing_requirements=(make_demand(11, 0, 2),))
    individual = make_individual(assignments=(make_assignment(slot_index=0),))

    result = CoverageScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 0.5


def test_overstaffing_reduces_score():
    problem = make_problem(
        slots=make_slots(1),
        workers=(make_worker(1, (11,), (0,)), make_worker(2, (11,), (0,))),
        staffing_requirements=(make_demand(11, 0, 1),),
    )
    individual = make_individual(
        assignments=(
            make_assignment(worker_id=1),
            make_assignment(worker_id=2),
        )
    )

    result = CoverageScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 0.0


def test_zero_demand_row_penalizes_assignments():
    problem = make_problem(staffing_requirements=(make_demand(11, 0, 0),))
    individual = make_individual(assignments=(make_assignment(slot_index=0),))

    result = CoverageScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 0.0


def test_empty_schedule_with_demand_scores_zero():
    problem = make_problem()

    result = CoverageScorer().score(make_input(problem, make_individual()))

    assert result.updates[0].score == 0.0


def test_empty_schedule_without_demand_scores_one():
    problem = make_problem(staffing_requirements=())

    result = CoverageScorer().score(make_input(problem, make_individual()))

    assert result.updates[0].score == 1.0


def test_assignments_without_demand_are_ignored():
    problem = make_problem(
        slots=make_slots(2),
        jobs=(make_job(11), make_job(12)),
        workers=(make_worker(1, (11, 12), (0, 1)),),
        staffing_requirements=(make_demand(11, 0, 1),),
    )
    individual = make_individual(
        assignments=(
            make_assignment(job_id=11, slot_index=0),
            make_assignment(job_id=12, slot_index=1),
        )
    )

    result = CoverageScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 1.0


def test_overstaffing_weight_is_configurable():
    problem = make_problem(
        slots=make_slots(1),
        workers=(make_worker(1, (11,), (0,)), make_worker(2, (11,), (0,))),
        staffing_requirements=(make_demand(11, 0, 1),),
    )
    individual = make_individual(
        assignments=(
            make_assignment(worker_id=1),
            make_assignment(worker_id=2),
        )
    )
    scorer = CoverageScorer(CoverageScorerConfig(overstaffing_weight=0.0))

    result = scorer.score(make_input(problem, individual))

    assert result.updates[0].score == 1.0


def test_scorer_does_not_mutate_input():
    score_input = make_input(
        make_problem(), make_individual(assignments=(make_assignment(),))
    )
    before = score_input.model_dump(mode="json")

    CoverageScorer().score(score_input)

    assert score_input.model_dump(mode="json") == before
