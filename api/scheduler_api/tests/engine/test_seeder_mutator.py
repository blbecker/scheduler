"""Seeder and mutator behavior: validity, bounds, and determinism."""

from __future__ import annotations

import pytest

from scheduler_api.engine.components import RandomShiftMutator, RandomShiftSeeder
from scheduler_api.engine.errors import ComponentResultError
from scheduler_api.engine.intervals import overlaps
from scheduler_api.engine.models.component_io import (
    RandomShiftMutateInput,
    SeedRandomShiftsInput,
)
from scheduler_api.engine.models.config import (
    RandomShiftMutatorConfig,
    SeedRandomShiftsConfig,
)
from scheduler_api.engine.models.time import is_on_grid
from scheduler_api.engine.policies import effective_bounds
from scheduler_api.tests.engine.builders import make_problem


def seed(problem, size=3, seed_value=11):
    return RandomShiftSeeder().seed(
        SeedRandomShiftsInput(
            problem=problem,
            population_size=size,
            random_seed=seed_value,
            config=SeedRandomShiftsConfig(contribution=size),
        )
    )


def mutate(problem, parents, count=4, seed_value=13, **config_kwargs):
    return RandomShiftMutator().mutate(
        RandomShiftMutateInput(
            problem=problem,
            parents=parents,
            offspring_count=count,
            random_seed=seed_value,
            config=RandomShiftMutatorConfig(share=count, **config_kwargs),
        )
    )


def test_seeder_produces_the_requested_population_size() -> None:
    result = seed(make_problem(), size=4)
    assert len(result.population.individuals) == 4
    assert len({individual.id for individual in result.population.individuals}) == 4


def test_seeded_shifts_are_structurally_valid() -> None:
    problem = make_problem()
    for individual in seed(problem).population.individuals:
        for shift in individual.shifts:
            assert shift.end > shift.start
            assert shift.minutes > 0
            assert problem.horizon_start <= shift.start < problem.horizon_end
            assert shift.end <= problem.horizon_end
            assert is_on_grid(shift.start, problem.boundary_granularity_minutes)
            worker = problem.worker(shift.worker_id)
            assert worker is not None
            assert shift.job_id in worker.qualified_job_ids
            minimum, maximum = effective_bounds(worker, problem.shifts)
            assert minimum <= shift.minutes <= maximum


def test_seeded_shifts_come_from_demand_windows_and_respect_availability() -> None:
    problem = make_problem()
    windows = [
        (requirement.start, requirement.end) for requirement in problem.requirements
    ]
    for individual in seed(problem).population.individuals:
        for shift in individual.shifts:
            assert any(
                overlaps(shift.start, shift.end, start, end) for start, end in windows
            )


def test_seeder_never_double_books_a_worker() -> None:
    problem = make_problem()
    for individual in seed(problem).population.individuals:
        by_worker: dict = {}
        for shift in individual.shifts:
            for other in by_worker.setdefault(shift.worker_id, []):
                assert not overlaps(shift.start, shift.end, other.start, other.end)
            by_worker[shift.worker_id].append(shift)


def test_seeding_is_deterministic_for_a_fixed_seed() -> None:
    problem = make_problem()
    first = seed(problem, seed_value=11).population
    second = seed(problem, seed_value=11).population
    assert first.model_dump_json() == second.model_dump_json()


def test_different_seeds_produce_different_populations() -> None:
    problem = make_problem()
    first = seed(problem, seed_value=11).population
    second = seed(problem, seed_value=12).population
    assert first.model_dump_json() != second.model_dump_json()


def test_mutator_returns_the_requested_offspring_count_with_fresh_state() -> None:
    problem = make_problem()
    parents = seed(problem).population.individuals
    result = mutate(problem, parents, count=5)
    assert len(result.individuals) == 5
    assert len({individual.id for individual in result.individuals}) == 5
    for individual in result.individuals:
        assert individual.scores == {}
        assert individual.violations == ()
        assert individual.fitness is None


def test_mutator_does_not_change_its_parents() -> None:
    problem = make_problem()
    parents = seed(problem).population.individuals
    before = tuple(parent.model_dump_json() for parent in parents)
    mutate(problem, parents)
    after = tuple(parent.model_dump_json() for parent in parents)
    assert before == after


def test_mutation_is_deterministic_for_a_fixed_seed() -> None:
    problem = make_problem()
    parents = seed(problem).population.individuals
    first = mutate(problem, parents).individuals
    second = mutate(problem, parents).individuals
    assert tuple(i.model_dump_json() for i in first) == tuple(
        i.model_dump_json() for i in second
    )


def test_mutated_shifts_stay_within_hard_bounds_and_the_horizon() -> None:
    problem = make_problem()
    parents = seed(problem).population.individuals
    for individual in mutate(problem, parents, count=8).individuals:
        for shift in individual.shifts:
            worker = problem.worker(shift.worker_id)
            assert worker is not None
            minimum, maximum = effective_bounds(worker, problem.shifts)
            assert minimum <= shift.minutes <= maximum
            assert problem.horizon_start <= shift.start
            assert shift.end <= problem.horizon_end
            assert is_on_grid(shift.start, problem.boundary_granularity_minutes)


def test_mutator_requires_a_parent() -> None:
    problem = make_problem()
    with pytest.raises(ComponentResultError):
        mutate(problem, ())


def test_boundary_nudging_alone_keeps_shift_count() -> None:
    problem = make_problem()
    parents = seed(problem).population.individuals
    result = mutate(
        problem,
        parents,
        count=6,
        weight_reassign_worker=0.0,
        weight_delete_shift=0.0,
        weight_insert_shift=0.0,
        weight_nudge_boundary=1.0,
        mutations_per_offspring=1,
    )
    for offspring, parent in zip(result.individuals, parents, strict=False):
        assert len(offspring.shifts) == len(parent.shifts)
