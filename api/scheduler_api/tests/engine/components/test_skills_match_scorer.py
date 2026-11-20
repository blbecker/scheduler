from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers.skills_match import (
    SkillsMatchScorer,
)
from scheduler_api.engine.models.component_config import (
    SkillsMatchScorerConfig,
)
from scheduler_api.engine.models.component_io import ScoreInput
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.scores import ViolationCode
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


def test_valid_assignments_score_one_and_have_no_violations():
    problem = make_problem()
    individual = make_individual(
        assignments=(make_assignment(slot_index=0), make_assignment(slot_index=1))
    )

    result = SkillsMatchScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 1.0
    assert result.updates[0].violations == ()


def test_unavailable_worker_is_a_violation():
    problem = make_problem(workers=(make_worker(1, (11,), (0,)),))
    individual = make_individual(assignments=(make_assignment(slot_index=1),))

    result = SkillsMatchScorer().score(make_input(problem, individual))

    codes = [v.code for v in result.updates[0].violations]
    assert codes == [ViolationCode.UNAVAILABLE_WORKER]
    assert result.updates[0].score == 0.0


def test_unqualified_worker_is_a_violation():
    problem = make_problem(
        jobs=(make_job(11), make_job(12)),
        workers=(make_worker(1, (12,), (0, 1, 2, 3)),),
    )
    individual = make_individual(assignments=(make_assignment(job_id=11),))

    result = SkillsMatchScorer().score(make_input(problem, individual))

    assert result.updates[0].violations[0].code is (ViolationCode.UNQUALIFIED_WORKER)


def test_unknown_references_are_violations():
    problem = make_problem()
    individual = make_individual(
        assignments=(
            make_assignment(worker_id=99),
            make_assignment(job_id=99, slot_index=1),
            make_assignment(slot_index=99),
        )
    )

    result = SkillsMatchScorer().score(make_input(problem, individual))

    codes = [v.code for v in result.updates[0].violations]
    assert codes == [
        ViolationCode.UNKNOWN_WORKER,
        ViolationCode.UNKNOWN_JOB,
        ViolationCode.SLOT_OUT_OF_RANGE,
    ]


def test_empty_schedule_scores_one():
    problem = make_problem()
    individual = make_individual(assignments=())

    result = SkillsMatchScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 1.0
    assert result.updates[0].violations == ()


def test_availability_check_can_be_disabled():
    problem = make_problem(workers=(make_worker(1, (11,), (0,)),))
    individual = make_individual(assignments=(make_assignment(slot_index=1),))
    scorer = SkillsMatchScorer(SkillsMatchScorerConfig(check_availability=False))

    result = scorer.score(make_input(problem, individual))

    assert result.updates[0].score == 1.0
    assert result.updates[0].violations == ()


def test_score_is_eligible_fraction():
    problem = make_problem(workers=(make_worker(1, (11,), (0,)),))
    individual = make_individual(
        assignments=(
            make_assignment(slot_index=0),
            make_assignment(slot_index=1),
        )
    )

    result = SkillsMatchScorer().score(make_input(problem, individual))

    assert result.updates[0].score == 0.5


def test_scorer_does_not_mutate_input():
    score_input = make_input(
        make_problem(),
        make_individual(assignments=(make_assignment(),)),
    )
    before = score_input.model_dump(mode="json")

    SkillsMatchScorer().score(score_input)

    assert score_input.model_dump(mode="json") == before


def test_violation_carries_assignment_context():
    individual = make_individual(
        assignments=(make_assignment(worker_id=7, job_id=11, slot_index=2),)
    )
    problem = make_problem(
        workers=(make_worker(1, (11,), (0, 1, 2, 3)),),
        jobs=(make_job(11),),
    )

    result = SkillsMatchScorer().score(make_input(problem, individual))

    violation = result.updates[0].violations[0]
    assert violation.worker_id == UUID(int=7)
    assert violation.job_id == UUID(int=11)
    assert violation.slot_index == 2
