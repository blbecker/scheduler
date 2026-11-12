"""Scorer behavior: scores on a 0-100 scale plus structured violations."""

from __future__ import annotations

from uuid import UUID

import pytest

from scheduler_api.engine.components import (
    AvailabilityScorer,
    CoverageScorer,
    DoubleBookingScorer,
    OverstaffingScorer,
    ScheduleLimitsScorer,
    ShiftLengthScorer,
    SkillsMatchScorer,
)
from scheduler_api.engine.models.component_io import (
    AvailabilityScoreInput,
    CoverageScoreInput,
    DoubleBookingScoreInput,
    OverstaffingScoreInput,
    ScheduleLimitsScoreInput,
    ShiftLengthScoreInput,
    SkillsMatchScoreInput,
)
from scheduler_api.engine.models.config import (
    AvailabilityScorerConfig,
    CoverageScorerConfig,
    DoubleBookingScorerConfig,
    OverstaffingScorerConfig,
    ScheduleLimitsScorerConfig,
    ShiftLengthScorerConfig,
    SkillsMatchScorerConfig,
)
from scheduler_api.engine.models.problem import (
    CoverageRequirement,
    JobInfo,
    ScheduleLimits,
)
from scheduler_api.engine.models.scores import ViolationCode
from scheduler_api.tests.engine.builders import (
    JOB_COOK,
    JOB_HOST,
    WORKER_1,
    WORKER_2,
    at,
    make_individual,
    make_problem,
    make_shift,
    make_window,
    make_worker,
)


UUID_ONE = UUID(int=501)
UUID_TWO = UUID(int=502)


def coverage(problem, individual):
    return CoverageScorer().score(
        CoverageScoreInput(
            problem=problem, individuals=(individual,), config=CoverageScorerConfig()
        )
    )


def test_coverage_is_full_when_every_required_minute_is_worked() -> None:
    problem = make_problem()
    individual = make_individual(
        (
            make_shift(WORKER_1, JOB_COOK, 8, 16),
            make_shift(WORKER_2, JOB_COOK, 8, 16),
        )
    )
    result = coverage(problem, individual)
    assert result.scores[individual.id] == pytest.approx(100.0)
    assert result.violations[individual.id] == ()


def test_coverage_is_zero_with_no_shifts() -> None:
    problem = make_problem()
    individual = make_individual()
    assert coverage(problem, individual).scores[individual.id] == pytest.approx(0.0)


def test_coverage_is_half_with_one_of_two_workers() -> None:
    problem = make_problem()
    individual = make_individual((make_shift(WORKER_1, JOB_COOK, 8, 16),))
    assert coverage(problem, individual).scores[individual.id] == pytest.approx(50.0)


def test_coverage_sums_simultaneous_windows() -> None:
    problem = make_problem(
        requirements=(
            CoverageRequirement(
                job_id=JOB_COOK, start=at(8), end=at(12), required_workers=1
            ),
            CoverageRequirement(
                job_id=JOB_COOK, start=at(10), end=at(14), required_workers=1
            ),
        )
    )
    individual = make_individual((make_shift(WORKER_1, JOB_COOK, 8, 12),))
    assert coverage(problem, individual).scores[individual.id] == pytest.approx(50.0)


def test_shift_outside_demand_is_a_violation() -> None:
    problem = make_problem()
    individual = make_individual((make_shift(WORKER_1, JOB_COOK, 20, 22),))
    result = coverage(problem, individual)
    codes = {violation.code for violation in result.violations[individual.id]}
    assert ViolationCode.SHIFT_OUTSIDE_DEMAND in codes


def test_shift_for_unknown_job_is_a_reference_violation() -> None:
    problem = make_problem(jobs=(JobInfo(job_id=JOB_COOK, name="Cook"),))
    individual = make_individual((make_shift(WORKER_1, JOB_HOST, 8, 12),))
    result = coverage(problem, individual)
    codes = {violation.code for violation in result.violations[individual.id]}
    assert ViolationCode.UNKNOWN_REFERENCE in codes


def test_overstaffing_penalizes_excess_minutes() -> None:
    problem = make_problem(
        requirements=(
            CoverageRequirement(
                job_id=JOB_COOK, start=at(8), end=at(12), required_workers=1
            ),
        )
    )
    individual = make_individual(
        (
            make_shift(WORKER_1, JOB_COOK, 8, 12),
            make_shift(WORKER_2, JOB_COOK, 8, 12),
        )
    )
    result = OverstaffingScorer().score(
        OverstaffingScoreInput(
            problem=problem,
            individuals=(individual,),
            config=OverstaffingScorerConfig(),
        )
    )
    assert result.scores[individual.id] == pytest.approx(0.0)


def test_overstaffing_scores_full_without_shifts() -> None:
    problem = make_problem()
    individual = make_individual()
    result = OverstaffingScorer().score(
        OverstaffingScoreInput(
            problem=problem,
            individuals=(individual,),
            config=OverstaffingScorerConfig(),
        )
    )
    assert result.scores[individual.id] == pytest.approx(100.0)


def test_skills_match_reports_unqualified_workers() -> None:
    problem = make_problem(
        workers=(
            make_worker(WORKER_1, jobs=frozenset({JOB_HOST})),
            make_worker(WORKER_2),
        )
    )
    individual = make_individual(
        (
            make_shift(WORKER_1, JOB_COOK, 8, 12),
            make_shift(WORKER_2, JOB_COOK, 8, 12),
        )
    )
    result = SkillsMatchScorer().score(
        SkillsMatchScoreInput(
            problem=problem, individuals=(individual,), config=SkillsMatchScorerConfig()
        )
    )
    assert result.scores[individual.id] == pytest.approx(50.0)
    codes = {violation.code for violation in result.violations[individual.id]}
    assert codes == {ViolationCode.WORKER_UNQUALIFIED}


def test_shift_length_hard_bounds_are_violations() -> None:
    problem = make_problem()
    individual = make_individual((make_shift(WORKER_1, JOB_COOK, 8, 9),))
    result = ShiftLengthScorer().score(
        ShiftLengthScoreInput(
            problem=problem, individuals=(individual,), config=ShiftLengthScorerConfig()
        )
    )
    codes = {violation.code for violation in result.violations[individual.id]}
    assert ViolationCode.SHIFT_TOO_SHORT in codes


def test_shift_length_preferences_cost_score_without_violations() -> None:
    problem = make_problem(
        workers=(make_worker(WORKER_1, preferred_minimum_shift_minutes=300),)
    )
    individual = make_individual((make_shift(WORKER_1, JOB_COOK, 8, 12),))
    result = ShiftLengthScorer().score(
        ShiftLengthScoreInput(
            problem=problem, individuals=(individual,), config=ShiftLengthScorerConfig()
        )
    )
    assert result.violations[individual.id] == ()
    assert result.scores[individual.id] == pytest.approx(75.0)


def test_availability_reports_minutes_outside_windows() -> None:
    problem = make_problem(
        workers=(make_worker(WORKER_1, availability=(make_window(8, 12),)),)
    )
    individual = make_individual((make_shift(WORKER_1, JOB_COOK, 10, 14),))
    result = AvailabilityScorer().score(
        AvailabilityScoreInput(
            problem=problem,
            individuals=(individual,),
            config=AvailabilityScorerConfig(),
        )
    )
    assert result.scores[individual.id] == pytest.approx(50.0)
    codes = {violation.code for violation in result.violations[individual.id]}
    assert codes == {ViolationCode.WORKER_UNAVAILABLE}


def test_double_booking_reports_overlaps() -> None:
    problem = make_problem()
    individual = make_individual(
        (
            make_shift(WORKER_1, JOB_COOK, 8, 12, shift_id=None),
            make_shift(WORKER_1, JOB_COOK, 11, 15, shift_id=None),
        )
    )
    result = DoubleBookingScorer().score(
        DoubleBookingScoreInput(
            problem=problem,
            individuals=(individual,),
            config=DoubleBookingScorerConfig(),
        )
    )
    codes = {violation.code for violation in result.violations[individual.id]}
    assert codes == {ViolationCode.WORKER_DOUBLE_BOOKED}
    assert result.scores[individual.id] < 100.0


def test_schedule_limits_reports_weekly_hours() -> None:
    problem = make_problem(limits=ScheduleLimits(maximum_hours_per_week=10))
    individual = make_individual(
        (
            make_shift(WORKER_1, JOB_COOK, 8, 16, day=0, shift_id=None),
            make_shift(WORKER_1, JOB_COOK, 8, 12, day=1, shift_id=None),
        )
    )
    result = ScheduleLimitsScorer().score(
        ScheduleLimitsScoreInput(
            problem=problem,
            individuals=(individual,),
            config=ScheduleLimitsScorerConfig(),
        )
    )
    codes = {violation.code for violation in result.violations[individual.id]}
    assert ViolationCode.WEEKLY_HOURS_EXCEEDED in codes


def test_schedule_limits_reports_shifts_per_day() -> None:
    problem = make_problem(limits=ScheduleLimits(maximum_shifts_per_day=1))
    individual = make_individual(
        (
            make_shift(WORKER_1, JOB_COOK, 8, 10, shift_id=None),
            make_shift(WORKER_1, JOB_COOK, 12, 14, shift_id=None),
        )
    )
    result = ScheduleLimitsScorer().score(
        ScheduleLimitsScoreInput(
            problem=problem,
            individuals=(individual,),
            config=ScheduleLimitsScorerConfig(),
        )
    )
    codes = {violation.code for violation in result.violations[individual.id]}
    assert ViolationCode.SHIFTS_PER_DAY_EXCEEDED in codes


def test_schedule_limits_score_full_when_no_caps_configured() -> None:
    problem = make_problem()
    individual = make_individual((make_shift(WORKER_1, JOB_COOK, 8, 16),))
    result = ScheduleLimitsScorer().score(
        ScheduleLimitsScoreInput(
            problem=problem,
            individuals=(individual,),
            config=ScheduleLimitsScorerConfig(),
        )
    )
    assert result.scores[individual.id] == pytest.approx(100.0)
    assert result.violations[individual.id] == ()


def test_every_scorer_scores_every_individual() -> None:
    problem = make_problem()
    individuals = (
        make_individual(
            (make_shift(WORKER_1, JOB_COOK, 8, 16),), individual_id=UUID_ONE
        ),
        make_individual(
            (make_shift(WORKER_2, JOB_COOK, 8, 16),), individual_id=UUID_TWO
        ),
    )
    scorers = (
        (CoverageScorer(), CoverageScoreInput, CoverageScorerConfig()),
        (OverstaffingScorer(), OverstaffingScoreInput, OverstaffingScorerConfig()),
        (SkillsMatchScorer(), SkillsMatchScoreInput, SkillsMatchScorerConfig()),
        (ShiftLengthScorer(), ShiftLengthScoreInput, ShiftLengthScorerConfig()),
        (AvailabilityScorer(), AvailabilityScoreInput, AvailabilityScorerConfig()),
        (DoubleBookingScorer(), DoubleBookingScoreInput, DoubleBookingScorerConfig()),
        (
            ScheduleLimitsScorer(),
            ScheduleLimitsScoreInput,
            ScheduleLimitsScorerConfig(),
        ),
    )
    for scorer, input_type, config in scorers:
        result = scorer.score(
            input_type(problem=problem, individuals=individuals, config=config)
        )
        assert set(result.scores) == {UUID_ONE, UUID_TWO}
        assert all(0.0 <= value <= 100.0 for value in result.scores.values())
