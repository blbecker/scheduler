import random
from typing import List
from scheduler_api.domain.schedule import Schedule
from scheduler_api.domain.population import Population
from scheduler_api.domain.schedule_layout import ScheduleLayout
from uuid import uuid4


def generate_initial_population(layout: ScheduleLayout, size: int = 100) -> Population:
    population = Population(
        generation=0,
        layout_id=layout.id,
    )

    for i in range(size):
        schedule = Schedule(
            name=f"Schedule_{i}",
            fitness=random.uniform(0.0, 1.0),
        )
        population.schedules.append(schedule)

    return population


def score_population(population: Population) -> Population:
    for schedule in population.schedules:
        if schedule.fitness is None:
            schedule.fitness = random.uniform(0.0, 1.0)
    return population


def mutate_population(population: Population, mutation_rate: float = 0.1) -> Population:
    for schedule in population.schedules:
        if random.random() < mutation_rate:
            schedule.fitness = max(
                0.0, min(1.0, schedule.fitness + random.uniform(-0.1, 0.1))
            )
    return population


def breed_population(population: Population, crossover_rate: float = 0.8) -> Population:
    if len(population.schedules) < 2:
        return population

    sorted_schedules = sorted(
        population.schedules, key=lambda s: s.fitness or 0.0, reverse=True
    )
    offspring = []

    for i in range(0, len(sorted_schedules) - 1, 2):
        parent1 = sorted_schedules[i]
        parent2 = sorted_schedules[i + 1]

        if random.random() < crossover_rate:
            child_fitness = ((parent1.fitness or 0.0) + (parent2.fitness or 0.0)) / 2.0
            child = Schedule(
                name=f"Child_{i//2}",
                fitness=child_fitness,
            )
            offspring.append(child)

    population.schedules.extend(offspring)
    return population


def cull_population(population: Population, target_size: int = 100) -> Population:
    if len(population.schedules) <= target_size:
        return population

    sorted_schedules = sorted(
        population.schedules, key=lambda s: s.fitness or 0.0, reverse=True
    )
    population.schedules = sorted_schedules[:target_size]
    return population


def select_best_schedule(population: Population) -> Schedule:
    return population.get_best_schedule()
