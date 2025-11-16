from scheduler_api.genetic.population import generate_initial_population
from scheduler_api.genetic.mutation import mutate_population


def test_mutate_population(simple_schedule_template):
    pop = generate_initial_population(simple_schedule_template, size=5)
    mutated = mutate_population(pop, mutation_rate=1.0)  # force mutation path

    assert len(mutated.individuals) == 5
    for i in range(5):
        assert mutated.individuals[i].schedule is not pop.individuals[i].schedule
