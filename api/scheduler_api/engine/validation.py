from __future__ import annotations

from scheduler_api.engine.exceptions import InvalidIndividualError
from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.problem import SchedulingProblem


def validate_individual_structure(
    individual: Individual,
    problem: SchedulingProblem,
) -> None:
    """Validate that every assignment references known problem entities."""

    worker_ids = {worker.worker_id for worker in problem.workers}
    job_ids = {job.job_id for job in problem.jobs}
    seen: set[tuple[object, object, int]] = set()

    for assignment in individual.assignments:
        if assignment.worker_id not in worker_ids:
            raise InvalidIndividualError(
                f"individual {individual.id} references unknown worker "
                f"{assignment.worker_id}"
            )
        if assignment.job_id not in job_ids:
            raise InvalidIndividualError(
                f"individual {individual.id} references unknown job "
                f"{assignment.job_id}"
            )
        if assignment.slot_index >= problem.slot_count:
            raise InvalidIndividualError(
                f"individual {individual.id} references unknown slot "
                f"{assignment.slot_index}"
            )
        key = (
            assignment.worker_id,
            assignment.job_id,
            assignment.slot_index,
        )
        if key in seen:
            raise InvalidIndividualError(
                f"individual {individual.id} contains duplicate assignments"
            )
        seen.add(key)


def validate_population_structure(
    population: Population,
    problem: SchedulingProblem,
) -> None:
    for individual in population.individuals:
        validate_individual_structure(individual, problem)
