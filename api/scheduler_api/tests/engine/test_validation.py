from __future__ import annotations

import pytest

from scheduler_api.engine.exceptions import InvalidIndividualError
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.validation import (
    validate_individual_structure,
    validate_population_structure,
)
from scheduler_api.tests.engine.factories import (
    make_assignment,
    make_individual,
    make_problem,
)


def test_valid_individual_passes_structure_validation():
    problem = make_problem()
    individual = make_individual(assignments=(make_assignment(slot_index=0),))

    validate_individual_structure(individual, problem)


def test_unknown_worker_is_rejected():
    problem = make_problem()
    individual = make_individual(assignments=(make_assignment(worker_id=9),))

    with pytest.raises(InvalidIndividualError, match="unknown worker"):
        validate_individual_structure(individual, problem)


def test_unknown_job_is_rejected():
    problem = make_problem()
    individual = make_individual(assignments=(make_assignment(job_id=99),))

    with pytest.raises(InvalidIndividualError, match="unknown job"):
        validate_individual_structure(individual, problem)


def test_unknown_slot_is_rejected():
    problem = make_problem()
    individual = make_individual(assignments=(make_assignment(slot_index=9),))

    with pytest.raises(InvalidIndividualError, match="unknown slot"):
        validate_individual_structure(individual, problem)


def test_population_validation_walks_every_individual():
    problem = make_problem()
    population = Population(
        individuals=(
            make_individual(
                individual_id=1,
                assignments=(make_assignment(slot_index=0),),
            ),
            make_individual(
                individual_id=2,
                assignments=(make_assignment(worker_id=9, slot_index=0),),
            ),
        )
    )

    with pytest.raises(InvalidIndividualError):
        validate_population_structure(population, problem)
