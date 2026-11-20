from __future__ import annotations

from scheduler_api.engine.components.seeders.random import (
    RandomScheduleSeeder,
)
from scheduler_api.engine.models.component_io import SeedInput
from scheduler_api.tests.engine.factories import (
    make_demand,
    make_job,
    make_problem,
    make_slots,
    make_worker,
)


def make_seed_input(problem=None, population_size=3, rng_seed=7):
    return SeedInput(
        category="seeder",
        problem=problem or make_problem(),
        population_size=population_size,
        rng_seed=rng_seed,
    )


def test_seeder_returns_requested_population_size():
    result = RandomScheduleSeeder().seed(make_seed_input(population_size=5))

    assert len(result.population.individuals) == 5


def test_seeder_is_deterministic_for_fixed_seed():
    seeder = RandomScheduleSeeder()
    first = seeder.seed(make_seed_input())
    second = seeder.seed(make_seed_input())

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_seeder_only_assigns_available_qualified_workers():
    slots = make_slots(4)
    job = make_job(1)
    problem = make_problem(
        slots=slots,
        jobs=(job,),
        workers=(
            make_worker(1, (1,), (0, 1)),
            make_worker(2, (1,), (1, 2)),
        ),
        staffing_requirements=(
            make_demand(1, 0, 1),
            make_demand(1, 1, 1),
            make_demand(1, 2, 1),
            make_demand(1, 3, 1),
        ),
    )
    result = RandomScheduleSeeder().seed(make_seed_input(problem=problem))

    for individual in result.population.individuals:
        seen: set[tuple[int, object]] = set()
        for assignment in individual.assignments:
            worker = next(
                w for w in problem.workers if w.worker_id == assignment.worker_id
            )
            assert assignment.slot_index in worker.available_slot_indices
            assert assignment.job_id in worker.qualified_job_ids
            key = (assignment.slot_index, assignment.worker_id)
            assert key not in seen
            seen.add(key)


def test_seeder_leaves_slots_understaffed_when_no_worker_is_eligible():
    slots = make_slots(2)
    job = make_job(1)
    problem = make_problem(
        slots=slots,
        jobs=(job,),
        workers=(make_worker(1, (1,), (1,)),),
        staffing_requirements=(make_demand(1, 0, 1),),
    )
    result = RandomScheduleSeeder().seed(make_seed_input(problem=problem))

    assert all(not i.assignments for i in result.population.individuals)


def test_seeder_does_not_mutate_input():
    seed_input = make_seed_input()
    before = seed_input.model_dump(mode="json")

    RandomScheduleSeeder().seed(seed_input)

    assert seed_input.model_dump(mode="json") == before
