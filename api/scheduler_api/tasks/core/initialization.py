"""Initialization pure functions for solve context and population."""

import logging
from typing import Any
from uuid import UUID
from datetime import datetime

from scheduler_api.dto.solve_context import ScheduleSolveContextDTO
from scheduler_api.dto.population import PopulationDTO, CandidateDTO
from scheduler_api.dto.solve_components import SeederDTO
from scheduler_api.engine.interfaces import Seeder

logger = logging.getLogger(__name__)


def initialize_context(
    template_id: UUID,
    parameters: dict[str, Any],
    shift_ids: list[UUID] | None = None,
    worker_ids: list[UUID] | None = None,
    skill_requirements: dict[UUID, list[UUID]] | None = None,
    worker_skills: dict[UUID, list[UUID]] | None = None,
) -> ScheduleSolveContextDTO:
    """
    Initialize solve context DTO.

    Args:
        template_id: Schedule template ID
        parameters: Solve parameters
        shift_ids: Optional list of shift IDs
        worker_ids: Optional list of worker IDs
        skill_requirements: Optional shift ID -> skill IDs mapping
        worker_skills: Optional worker ID -> skill IDs mapping

    Returns:
        Initialized ScheduleSolveContextDTO
    """
    # Convert UUIDs to strings for DTO
    context_dto = ScheduleSolveContextDTO(
        template_id=str(template_id),
        shift_ids=[str(sid) for sid in shift_ids] if shift_ids else [],
        worker_ids=[str(wid) for wid in worker_ids] if worker_ids else [],
        skill_requirements=(
            {
                str(sid): [str(skill_id) for skill_id in skills]
                for sid, skills in skill_requirements.items()
            }
            if skill_requirements
            else {}
        ),
        worker_skills=(
            {
                str(wid): [str(skill_id) for skill_id in skills]
                for wid, skills in worker_skills.items()
            }
            if worker_skills
            else {}
        ),
        parameters=parameters,
    )

    logger.info(f"Initialized context for template {template_id}")
    return context_dto


def create_initial_population(
    context_dto: ScheduleSolveContextDTO,
    population_size: int,
    seeder_dtos: list[dict],  # Serialized SeederDTO dicts
    component_classes: dict[str, Any],  # Mapping for seeder instantiation
) -> PopulationDTO:
    """
    Create initial population using seeders.

    Args:
        context_dto: Solve context
        population_size: Target population size
        seeder_dtos: List of seeder DTO dicts
        component_classes: Component class mapping for seeder instantiation

    Returns:
        Initial PopulationDTO
    """
    logger.info(f"Creating initial population of size {population_size}")

    if not seeder_dtos:
        # Create random initial population if no seeders
        return _create_random_initial_population(context_dto, population_size)

    # For now, use first seeder
    from scheduler_api.dto.solve_components import SeederDTO

    seeder_dto = SeederDTO(**seeder_dtos[0])

    # Instantiate seeder
    from .evolutionary import instantiate_component

    seeder = instantiate_component(seeder_dto, component_classes)

    # Generate initial genomes
    try:
        # Note: seeders expect domain context, not DTO
        # For now, pass DTO directly - seeder needs to handle it
        genomes = seeder.seed(context_dto, population_size)
    except Exception as e:
        logger.warning(f"Seeder {seeder.name} failed: {e}, using random population")
        return _create_random_initial_population(context_dto, population_size)

    # Create population DTO
    candidates = []
    for genome_data in genomes:
        candidate = CandidateDTO(
            genome_data=genome_data,
            fitness=0.0,
            generation=0,
            metadata={"type": "initial"},
        )
        candidates.append(candidate)

    population = PopulationDTO(generation=0, candidates=candidates)

    logger.info(f"Created initial population with {len(candidates)} candidates")
    return population


def _create_random_initial_population(
    context_dto: ScheduleSolveContextDTO, population_size: int
) -> PopulationDTO:
    """Create random initial population for testing."""
    candidates = []

    # Get shift and worker IDs from context
    shift_ids = [UUID(sid) for sid in context_dto.shift_ids]
    worker_ids = [UUID(wid) for wid in context_dto.worker_ids]

    for i in range(population_size):
        # Create random assignments
        assignments = {}
        for shift_id in shift_ids:
            if worker_ids and i % 2 == 0:  # Assign some workers
                worker_idx = i % len(worker_ids)
                assignments[str(shift_id)] = [str(worker_ids[worker_idx])]

        genome_data = {"assignments": assignments}

        candidate = CandidateDTO(
            genome_data=genome_data,
            fitness=0.0,
            generation=0,
            metadata={"type": "random_initial"},
        )
        candidates.append(candidate)

    population = PopulationDTO(generation=0, candidates=candidates)

    return population
