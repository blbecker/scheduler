"""Candidate mapping: violation aggregation and persistence-ready drafts."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.models.results import CandidateSchedule, ExecutionResult
from scheduler_api.engine.models.scores import Violation, ViolationCode
from scheduler_api.mappers.candidate_schedule_mapper import (
    summarise_violations,
    to_schedule_draft,
)
from scheduler_api.tests.engine.builders import (
    JOB_COOK,
    WORKER_1,
    WORKER_2,
    at,
    make_problem,
    make_shift,
)


def violation(
    code: ViolationCode, worker: UUID | None = None, detail: str = ""
) -> Violation:
    return Violation(code=code, worker_id=worker, job_id=JOB_COOK, detail=detail)


def test_violations_are_grouped_by_code_with_counts() -> None:
    summaries = summarise_violations(
        (
            violation(ViolationCode.WORKER_UNAVAILABLE, WORKER_1),
            violation(ViolationCode.WORKER_UNAVAILABLE, WORKER_2),
            violation(ViolationCode.WORKER_UNQUALIFIED, WORKER_1),
        )
    )
    assert [(summary.code, summary.count) for summary in summaries] == [
        (ViolationCode.WORKER_UNAVAILABLE, 2),
        (ViolationCode.WORKER_UNQUALIFIED, 1),
    ]


def test_violation_examples_are_capped() -> None:
    violations = tuple(
        violation(ViolationCode.WORKER_UNAVAILABLE, WORKER_1, f"case {index}")
        for index in range(10)
    )
    summary = summarise_violations(violations, example_limit=2)[0]
    assert summary.count == 10
    assert len(summary.examples) == 2
    assert summary.worker_ids == (WORKER_1,)


def test_violation_summaries_are_ordered_by_count_then_code() -> None:
    summaries = summarise_violations(
        (
            violation(ViolationCode.WORKER_UNQUALIFIED),
            violation(ViolationCode.WORKER_UNAVAILABLE),
            violation(ViolationCode.WORKER_UNAVAILABLE),
        )
    )
    assert [summary.code for summary in summaries] == [
        ViolationCode.WORKER_UNAVAILABLE,
        ViolationCode.WORKER_UNQUALIFIED,
    ]


def test_schedule_draft_carries_the_review_basis() -> None:
    problem = make_problem()
    shifts = (
        make_shift(WORKER_1, JOB_COOK, 8, 16),
        make_shift(WORKER_2, JOB_COOK, 8, 16),
    )
    candidate = CandidateSchedule(
        candidate_id=UUID(int=42),
        rank=1,
        shifts=shifts,
        fitness=87.5,
        scores={"coverage": 100.0, "skills_match": 75.0},
        violations=(violation(ViolationCode.WORKER_UNAVAILABLE, WORKER_1),),
        feasible=False,
    )
    result = ExecutionResult(
        execution_id=UUID(int=7),
        candidates=(candidate,),
        generation=3,
        termination_reason="reached generation limit of 4",
        random_seed=99,
    )
    draft = to_schedule_draft(candidate, result, problem)
    assert draft.execution_id == UUID(int=7)
    assert draft.candidate_id == UUID(int=42)
    assert draft.timezone == "America/Puerto_Rico"
    assert draft.fitness == 87.5
    assert draft.feasible is False
    assert draft.scores == {"coverage": 100.0, "skills_match": 75.0}
    assert [shift.duration_minutes for shift in draft.shifts] == [480, 480]
    assert draft.shifts[0].start == at(8)
    assert draft.shifts[0].start.tzinfo is not None
    assert draft.violation_count == 1
    assert draft.violations[0].code is ViolationCode.WORKER_UNAVAILABLE
    assert draft.random_seed == 99
    assert draft.termination_reason.startswith("reached generation limit")
