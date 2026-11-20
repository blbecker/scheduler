from __future__ import annotations

import pytest

from scheduler_api.engine.components.cullers.top_n import TopNCuller
from scheduler_api.engine.exceptions import PopulationSizeMismatchError
from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.component_io import CullInput
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.scores import Violation, ViolationCode
from scheduler_api.tests.engine.factories import make_individual, make_policy


def make_input(population, target_size=2, elites=()):
    return CullInput(
        category="culler",
        population=population,
        target_size=target_size,
        scoring_policy=make_policy(("coverage", 1.0)),
        elite_individuals=elites,
    )


def test_keeps_best_candidates():
    individuals = (
        make_individual(1, scores={"coverage": 0.2}),
        make_individual(2, scores={"coverage": 0.9}),
        make_individual(3, scores={"coverage": 0.5}),
    )

    result = TopNCuller().cull(
        make_input(Population(individuals=individuals), target_size=2)
    )

    assert [i.id for i in result.population.individuals] == [
        individuals[1].id,
        individuals[2].id,
    ]


def test_infeasible_candidate_ranks_after_feasible():
    feasible = make_individual(1, scores={"coverage": 0.0})
    infeasible = Individual(
        id=make_individual(2).id,
        assignments=(),
        scores={"coverage": 1.0},
        violations=(
            Violation(
                code=ViolationCode.UNQUALIFIED_WORKER,
                message="not qualified",
            ),
        ),
    )

    result = TopNCuller().cull(
        make_input(Population(individuals=(infeasible, feasible)), target_size=2)
    )

    assert result.population.individuals[0].id == feasible.id


def test_elite_is_injected_even_with_lower_score():
    best = make_individual(1, scores={"coverage": 0.9})
    second = make_individual(2, scores={"coverage": 0.8})
    elite = make_individual(99, scores={"coverage": 0.0})

    result = TopNCuller().cull(
        make_input(
            Population(individuals=(best, second)),
            target_size=2,
            elites=(elite,),
        )
    )

    ids = [i.id for i in result.population.individuals]
    assert elite.id in ids
    assert best.id in ids
    assert second.id not in ids


def test_too_few_candidates_is_rejected():
    with pytest.raises(PopulationSizeMismatchError):
        TopNCuller().cull(
            make_input(
                Population(individuals=(make_individual(1, scores={"coverage": 1.0}),)),
                target_size=2,
            )
        )


def test_more_elites_than_target_is_rejected():
    individuals = (
        make_individual(1, scores={"coverage": 1.0}),
        make_individual(2, scores={"coverage": 0.5}),
    )
    with pytest.raises(PopulationSizeMismatchError):
        TopNCuller().cull(
            make_input(
                Population(individuals=individuals),
                target_size=1,
                elites=individuals,
            )
        )


def test_elites_must_fit_when_all_selected_are_elite():
    first = make_individual(1, scores={"coverage": 1.0})
    second = make_individual(2, scores={"coverage": 0.5})
    with pytest.raises(PopulationSizeMismatchError):
        TopNCuller().cull(
            make_input(
                Population(individuals=(first,)),
                target_size=1,
                elites=(first, second),
            )
        )


def test_culler_does_not_mutate_input():
    cull_input = make_input(
        Population(
            individuals=(
                make_individual(1, scores={"coverage": 0.1}),
                make_individual(2, scores={"coverage": 0.9}),
            )
        )
    )
    before = cull_input.model_dump(mode="json")

    TopNCuller().cull(cull_input)

    assert cull_input.model_dump(mode="json") == before
