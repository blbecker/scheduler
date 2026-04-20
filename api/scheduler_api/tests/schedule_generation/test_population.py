from scheduler_api.genetic.population import (
    generate_initial_population,
    clone_schedule,
)
from scheduler_api.genetic.scoring import ScoreResult


def test_generate_initial_population(simple_schedule_template):
    pop = generate_initial_population(simple_schedule_template, size=5)
    assert len(pop.individuals) == 5
    assert all(ind.schedule is not simple_schedule_template for ind in pop.individuals)


def test_clone_schedule(simple_schedule_template):
    cloned = clone_schedule(simple_schedule_template)
    assert cloned is not simple_schedule_template
    assert cloned.model_dump() == simple_schedule_template.model_dump()


def test_population_scoring(simple_schedule_template):
    pop = generate_initial_population(simple_schedule_template, size=3)

    def dummy_scorer(schedule):
        return ScoreResult(score=10, ok=True)

    pop.score([dummy_scorer])

    for ind in pop.individuals:
        assert ind.score == 10
        assert ind.hard_fail is False
        assert ind.messages == []
