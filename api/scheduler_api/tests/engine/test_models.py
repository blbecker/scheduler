"""Engine DTOs: validation, canonicalization, and fitness."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError

from scheduler_api.engine.errors import ComponentResultError, ProblemValidationError
from scheduler_api.engine.models.fitness import FitnessConfig, compute_fitness
from scheduler_api.engine.models.genome import Individual, PlannedShift, Population
from scheduler_api.engine.models.problem import TimeWindow, validate_problem_context
from scheduler_api.engine.models.results import CandidateSchedule
from scheduler_api.engine.models.time import (
    ensure_minute_aligned,
    is_on_grid,
    snap_to_grid,
)
from scheduler_api.tests.engine.builders import (
    JOB_COOK,
    TZ,
    WORKER_1,
    WORKER_2,
    at,
    make_individual,
    make_problem,
    make_shift,
    rule,
)


def test_time_window_rejects_naive_datetimes() -> None:
    with pytest.raises(ValidationError):
        TimeWindow(start=datetime(2026, 11, 16, 8), end=datetime(2026, 11, 16, 12))


def test_time_window_rejects_inverted_intervals() -> None:
    with pytest.raises(ValidationError):
        TimeWindow(start=at(12), end=at(8))


def test_time_window_rejects_unaligned_minutes() -> None:
    with pytest.raises(ValidationError):
        TimeWindow(start=at(8) + timedelta(seconds=30), end=at(12))


def test_shift_rejects_zero_length() -> None:
    with pytest.raises(ValidationError):
        PlannedShift(
            shift_id=UUID(int=1),
            worker_id=WORKER_1,
            job_id=JOB_COOK,
            start=at(8),
            end=at(8),
        )


def test_individual_canonicalizes_shift_order() -> None:
    later = make_shift(WORKER_2, JOB_COOK, 12, 14)
    earlier = make_shift(WORKER_1, JOB_COOK, 8, 10)
    forward = make_individual((earlier, later))
    backward = make_individual((later, earlier))
    assert forward.shifts == backward.shifts
    assert forward.structural_key == backward.structural_key


def test_individual_rejects_out_of_range_scores() -> None:
    with pytest.raises(ValidationError):
        Individual(id=UUID(int=1), scores={"coverage": 140.0})


def test_individual_feasible_is_defined_by_violations() -> None:
    clean = make_individual()
    dirty = make_individual(violations=(rule("worker_unavailable"),))
    assert clean.feasible is True
    assert dirty.feasible is False


def test_population_rejects_duplicate_individual_ids() -> None:
    individual = make_individual(individual_id=UUID(int=7))
    with pytest.raises(ValidationError):
        Population(individuals=(individual, individual))


def test_fitness_config_rejects_negative_weights() -> None:
    with pytest.raises(ValidationError):
        FitnessConfig(weights={"coverage": -1.0})


def test_fitness_is_the_weighted_mean_of_scores() -> None:
    config = FitnessConfig(weights={"coverage": 1.0, "skills_match": 3.0})
    fitness = compute_fitness({"coverage": 100.0, "skills_match": 50.0}, config)
    assert fitness == pytest.approx((100.0 * 1 + 50.0 * 3) / 4)


def test_fitness_ignores_zero_weight_components() -> None:
    config = FitnessConfig(weights={"coverage": 1.0, "availability": 0.0})
    assert compute_fitness(
        {"coverage": 80.0, "availability": 0.0}, config
    ) == pytest.approx(80.0)


def test_fitness_defaults_missing_weights_to_one() -> None:
    assert compute_fitness({"coverage": 60.0}, FitnessConfig()) == pytest.approx(60.0)


def test_fitness_requires_at_least_one_weighted_score() -> None:
    with pytest.raises(ComponentResultError):
        compute_fitness(
            {"availability": 10.0}, FitnessConfig(weights={"availability": 0.0})
        )


def test_fitness_rejects_out_of_range_scores() -> None:
    with pytest.raises(ComponentResultError):
        compute_fitness({"coverage": 101.0}, FitnessConfig())


def test_candidate_schedule_rejects_out_of_range_fitness() -> None:
    with pytest.raises(ValidationError):
        CandidateSchedule(
            candidate_id=UUID(int=1), rank=1, fitness=120.0, feasible=True
        )


def test_validate_problem_context_rejects_empty_demand() -> None:
    problem = make_problem(requirements=())
    with pytest.raises(ProblemValidationError):
        validate_problem_context(problem)


def test_validate_problem_context_rejects_unknown_job_reference() -> None:
    problem = make_problem(
        workers=(
            make_problem()
            .workers[0]
            .model_copy(update={"qualified_job_ids": frozenset({UUID(int=999)})}),
        )
    )
    with pytest.raises(ProblemValidationError):
        validate_problem_context(problem)


def test_validate_problem_context_accepts_a_well_formed_problem() -> None:
    validate_problem_context(make_problem())


def test_snap_to_grid_moves_down_and_up() -> None:
    moment = at(8) + timedelta(minutes=7)
    assert snap_to_grid(moment, 15, direction="down") == at(8)
    assert snap_to_grid(moment, 15, direction="up") == at(8) + timedelta(minutes=15)
    assert is_on_grid(snap_to_grid(moment, 15, direction="up"), 15)


def test_ensure_minute_aligned_rejects_seconds() -> None:
    with pytest.raises(ValueError):
        ensure_minute_aligned(at(8) + timedelta(seconds=1), "start")


def test_problem_timezone_is_resolved() -> None:
    problem = make_problem()
    assert problem.tz == TZ
    assert problem.horizon_minutes == 2880
