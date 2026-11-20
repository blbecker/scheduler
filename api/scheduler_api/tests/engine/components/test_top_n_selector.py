from __future__ import annotations

from scheduler_api.engine.components.selectors.top_n import TopNSelector
from scheduler_api.engine.models.component_io import SelectInput
from scheduler_api.engine.models.population import Population
from scheduler_api.tests.engine.factories import make_individual, make_policy


def make_input(population, count=2):
    return SelectInput(
        category="selector",
        population=population,
        count=count,
        scoring_policy=make_policy(("coverage", 1.0)),
    )


def test_selects_highest_scoring_first():
    low = make_individual(1, scores={"coverage": 0.2})
    high = make_individual(2, scores={"coverage": 0.9})
    middle = make_individual(3, scores={"coverage": 0.5})
    select_input = make_input(Population(individuals=(low, high, middle)), count=2)

    result = TopNSelector().select(select_input)

    assert [i.id for i in result.selected.individuals] == [
        high.id,
        middle.id,
    ]


def test_prefers_feasible_over_infeasible():
    from scheduler_api.engine.models.assignment import Individual
    from scheduler_api.engine.models.scores import Violation, ViolationCode

    feasible = make_individual(1, scores={"coverage": 0.1})
    infeasible = Individual(
        id=make_individual(2).id,
        assignments=(),
        scores={"coverage": 1.0},
        violations=(
            Violation(
                code=ViolationCode.UNAVAILABLE_WORKER,
                message="not available",
            ),
        ),
    )
    select_input = make_input(Population(individuals=(infeasible, feasible)), count=1)

    result = TopNSelector().select(select_input)

    assert result.selected.individuals[0].id == feasible.id


def test_returns_fewer_when_population_is_smaller_than_count():
    individual = make_individual(1, scores={"coverage": 1.0})

    result = TopNSelector().select(
        make_input(Population(individuals=(individual,)), count=5)
    )

    assert len(result.selected.individuals) == 1


def test_selector_does_not_mutate_input():
    select_input = make_input(
        Population(
            individuals=(
                make_individual(1, scores={"coverage": 0.1}),
                make_individual(2, scores={"coverage": 0.9}),
            )
        )
    )
    before = select_input.model_dump(mode="json")

    TopNSelector().select(select_input)

    assert select_input.model_dump(mode="json") == before
