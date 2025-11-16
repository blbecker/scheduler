from scheduler_api.genetic.selection import select_survivors
from scheduler_api.genetic.population import Population, Individual
from scheduler_api.models import ScheduleTemplate
from uuid import uuid4


def make_ind(score, fail=False):
    sched = ScheduleTemplate(id=uuid4(), start_time=None, end_time=None, shifts=[])
    return Individual(schedule=sched, score=score, hard_fail=fail, messages=[])


def test_selection_elitism():
    inds = [
        make_ind(100),
        make_ind(90),
        make_ind(80, fail=True),  # hard fail, should sort to bottom
        make_ind(70),
    ]

    pop = Population(individuals=inds)
    survivors = select_survivors(population=pop, elitism=1)

    assert len(survivors.individuals) == len(inds)
    # Best non-failing individual with highest score should be preserved as elite
    assert survivors.individuals[0].score == 100
