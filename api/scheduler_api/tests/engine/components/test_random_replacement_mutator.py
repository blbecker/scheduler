from __future__ import annotations

import pytest

from scheduler_api.engine.components.mutators.random_replacement import (
    RandomReplacementMutator,
)
from scheduler_api.engine.exceptions import InvalidComponentInputError
from scheduler_api.engine.models.component_io import MutateInput
from scheduler_api.engine.models.population import Population
from scheduler_api.tests.engine.factories import (
    make_assignment,
    make_individual,
    make_problem,
    make_worker,
)


def make_input(problem, parents, offspring_count=2, rng_seed=5):
    return MutateInput(
        category="mutator",
        problem=problem,
        parents=parents,
        offspring_count=offspring_count,
        rng_seed=rng_seed,
    )


def test_returns_requested_offspring_count():
    problem = make_problem()
    parents = Population(
        individuals=(make_individual(1, assignments=(make_assignment(),)),)
    )

    result = RandomReplacementMutator().mutate(
        make_input(problem, parents, offspring_count=4)
    )

    assert len(result.offspring.individuals) == 4


def test_offspring_are_unscored():
    problem = make_problem()
    parent = make_individual(
        1,
        assignments=(make_assignment(),),
        scores={"coverage": 1.0},
    )

    result = RandomReplacementMutator().mutate(
        make_input(problem, Population(individuals=(parent,)))
    )

    for offspring in result.offspring.individuals:
        assert offspring.scores == {}
        assert offspring.violations == ()


def test_mutation_only_changes_worker():
    problem = make_problem(
        workers=(
            make_worker(1, (11,), (0, 1, 2, 3)),
            make_worker(2, (11,), (0, 1, 2, 3)),
        )
    )
    parent = make_individual(
        1, assignments=(make_assignment(worker_id=1, slot_index=0),)
    )

    result = RandomReplacementMutator().mutate(
        make_input(problem, Population(individuals=(parent,)), offspring_count=1)
    )

    assignment = result.offspring.individuals[0].assignments[0]
    assert assignment.job_id == parent.assignments[0].job_id
    assert assignment.slot_index == parent.assignments[0].slot_index
    assert assignment.worker_id in {
        parent.assignments[0].worker_id,
        make_worker(2).worker_id,
    }


def test_mutator_is_deterministic_for_fixed_seed():
    problem = make_problem()
    parents = Population(
        individuals=(
            make_individual(1, assignments=(make_assignment(),)),
            make_individual(2, assignments=(make_assignment(slot_index=1),)),
        )
    )
    mutator = RandomReplacementMutator()

    first = mutator.mutate(make_input(problem, parents, rng_seed=9))
    second = mutator.mutate(make_input(problem, parents, rng_seed=9))

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_empty_parents_with_offspring_is_rejected():
    with pytest.raises(InvalidComponentInputError):
        RandomReplacementMutator().mutate(
            make_input(
                make_problem(),
                Population(individuals=()),
                offspring_count=1,
            )
        )


def test_empty_parents_with_no_offspring_returns_empty():
    result = RandomReplacementMutator().mutate(
        make_input(
            make_problem(),
            Population(individuals=()),
            offspring_count=0,
        )
    )

    assert result.offspring.individuals == ()


def test_mutator_does_not_mutate_input():
    problem = make_problem()
    mutate_input = make_input(
        problem,
        Population(individuals=(make_individual(1, assignments=(make_assignment(),)),)),
    )
    before = mutate_input.model_dump(mode="json")

    RandomReplacementMutator().mutate(mutate_input)

    assert mutate_input.model_dump(mode="json") == before
