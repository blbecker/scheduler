"""Pure functions for evolutionary operations on DTOs."""

import logging
import random
from typing import Any, Type, TypeVar, Union
from uuid import uuid4

from scheduler_api.dto.population import PopulationDTO, CandidateDTO
from scheduler_api.dto.solve_components import (
    ScorerDTO,
    MutatorDTO,
    ConstraintDTO,
    SelectorDTO,
    SeederDTO,
)
from scheduler_api.dto.solve_context import ScheduleSolveContextDTO
from scheduler_api.engine.interfaces import (
    Scorable,
    GenomeOperator,
    Constraint,
    Selector,
    Seeder,
)

logger = logging.getLogger(__name__)

# Type variables
Component = TypeVar("Component", Scorable, GenomeOperator, Constraint, Selector, Seeder)


def instantiate_component(
    dto: Union[ScorerDTO, MutatorDTO, ConstraintDTO, SelectorDTO, SeederDTO],
    component_classes: dict[str, Type[Component]],
) -> Component:
    """Instantiate component from DTO using registered component classes."""
    component_type = dto.component_type.value
    if component_type not in component_classes:
        raise ValueError(f"Unknown component type: {component_type}")

    component_class = component_classes[component_type]
    return component_class(**dto.config)


def score_population(
    population_dto: PopulationDTO,
    scorer_dtos: list[ScorerDTO],
    constraint_dtos: list[ConstraintDTO],
    context_dto: ScheduleSolveContextDTO,
    component_classes: dict[str, Any],  # Accepts any component type
) -> tuple[PopulationDTO, dict[str, Any]]:
    """
    Score all candidates in population using scorers and constraints.

    Args:
        population_dto: Population to score
        scorer_dtos: List of scorer DTOs
        constraint_dtos: List of constraint DTOs
        context_dto: Solve context
        component_classes: Mapping of component type to class

    Returns:
        Tuple of (scored PopulationDTO, metrics dictionary)
    """
    logger.info(
        f"Scoring population with {len(scorer_dtos)} scorers, {len(constraint_dtos)} constraints"
    )

    # Instantiate components
    scorers = [instantiate_component(dto, component_classes) for dto in scorer_dtos]
    constraints = [
        instantiate_component(dto, component_classes) for dto in constraint_dtos
    ]

    scored_candidates = []
    metrics = {
        "candidates_scored": 0,
        "total_fitness": 0.0,
        "max_fitness": 0.0,
        "min_fitness": float("inf") if population_dto.candidates else 0.0,
    }

    # Convert context DTO to domain context if needed
    # For now, pass DTO directly - components need to handle DTO format
    for candidate in population_dto.candidates:
        total_score = 0.0
        score_breakdown = {}

        # Apply scorers
        for scorer in scorers:
            try:
                # Note: scorers need to work with genome_data dict
                score = scorer.score(candidate.genome_data, context_dto)
                total_score += score
                score_breakdown[scorer.name] = score
            except Exception as e:
                logger.warning(f"Scorer {scorer.name} failed: {e}")
                score_breakdown[scorer.name] = 0.0

        # Apply constraints (penalties)
        for constraint in constraints:
            try:
                penalty = constraint.penalty(candidate.genome_data, context_dto)
                total_score -= penalty
                score_breakdown[f"{constraint.name}_penalty"] = penalty
            except Exception as e:
                logger.warning(f"Constraint {constraint.name} failed: {e}")

        # Ensure fitness is non-negative
        fitness = max(0.0, total_score)

        # Update candidate
        scored_candidate = CandidateDTO(
            **candidate.model_dump(), fitness=fitness, score_breakdown=score_breakdown
        )
        scored_candidates.append(scored_candidate)

        # Update metrics
        metrics["candidates_scored"] += 1
        metrics["total_fitness"] += fitness
        metrics["max_fitness"] = max(metrics["max_fitness"], fitness)
        metrics["min_fitness"] = min(metrics["min_fitness"], fitness)

    # Calculate averages
    if population_dto.candidates:
        metrics["avg_fitness"] = metrics["total_fitness"] / len(
            population_dto.candidates
        )
        metrics["min_fitness"] = (
            metrics["min_fitness"] if metrics["min_fitness"] != float("inf") else 0.0
        )
    else:
        metrics["avg_fitness"] = 0.0
        metrics["min_fitness"] = 0.0

    # Create new population DTO
    scored_population = PopulationDTO(
        generation=population_dto.generation, candidates=scored_candidates
    )

    logger.info(f"Scoring complete: {metrics}")
    return scored_population, metrics


import json


# In the selection function, fix the elite_genomes set
def select_population(
    scored_population_dto: PopulationDTO,
    selector_dto: SelectorDTO,
    context_dto: ScheduleSolveContextDTO,
    component_classes: dict[str, Type[Selector]],
    elite_size: int,
    target_size: int,
) -> tuple[PopulationDTO, dict[str, Any]]:
    """
    Select candidates for next generation using selector.

    Args:
        scored_population_dto: Scored population to select from
        selector_dto: Selector DTO
        context_dto: Solve context
        component_classes: Mapping of component type to class
        elite_size: Number of elite candidates to preserve
        target_size: Target population size after selection

    Returns:
        Tuple of (selected PopulationDTO, metrics dictionary)
    """
    logger.info(
        f"Selecting population: elite_size={elite_size}, target_size={target_size}"
    )

    # Instantiate selector
    selector = instantiate_component(selector_dto, component_classes)

    # Create list of (genome_data, fitness) for selector
    genomes_with_fitness = [
        (candidate.genome_data, candidate.fitness)
        for candidate in scored_population_dto.candidates
    ]

    # Select candidates
    try:
        selected_genomes = selector.select(
            genomes_with_fitness, context_dto, target_size
        )
    except Exception as e:
        logger.error(f"Selector {selector.name} failed: {e}")
        # Fall back to simple top-N selection
        sorted_candidates = sorted(
            scored_population_dto.candidates, key=lambda c: c.fitness, reverse=True
        )
        selected_genomes = [c.genome_data for c in sorted_candidates[:target_size]]

    # Create selected candidates - we need to preserve elite status
    selected_candidates = []

    # First, preserve elites
    elites = scored_population_dto.get_top_n(elite_size)
    for elite in elites:
        selected_candidate = CandidateDTO(
            **elite.model_dump(), metadata={**elite.metadata, "type": "elite"}
        )
        selected_candidates.append(selected_candidate)

    # Then add remaining selected candidates
    elite_genome_strings = {json.dumps(c.genome_data, sort_keys=True) for c in elites}
    added_count = 0

    for genome_data in selected_genomes:
        if added_count >= target_size - elite_size:
            break

        # Skip if already elite
        genome_string = json.dumps(genome_data, sort_keys=True)
        if genome_string in elite_genome_strings:
            continue

        # Find original candidate with this genome
        original_candidate = None
        for candidate in scored_population_dto.candidates:
            if candidate.genome_data == genome_data:
                original_candidate = candidate
                break

        if original_candidate:
            selected_candidate = CandidateDTO(
                **original_candidate.model_dump(),
                metadata={**original_candidate.metadata, "type": "selected"},
            )
            selected_candidates.append(selected_candidate)
            added_count += 1

    # Create selected population
    selected_population = PopulationDTO(
        generation=scored_population_dto.generation, candidates=selected_candidates
    )

    metrics = {
        "elite_preserved": len(elites),
        "selected_count": len(selected_candidates),
        "target_size": target_size,
        "selector_used": selector_dto.name,
    }

    logger.info(f"Selection complete: {metrics}")
    return selected_population, metrics


def mutate_population(
    population_dto: PopulationDTO,
    mutator_dtos: list[MutatorDTO],
    context_dto: ScheduleSolveContextDTO,
    component_classes: dict[str, Type[GenomeOperator]],
    mutation_rate: float,
) -> tuple[PopulationDTO, dict[str, Any]]:
    """
    Apply mutation to population based on mutation rate.

    Args:
        population_dto: Population to mutate
        mutator_dtos: List of mutator DTOs
        context_dto: Solve context
        component_classes: Mapping of component type to class
        mutation_rate: Probability of mutation per candidate

    Returns:
        Tuple of (mutated PopulationDTO, metrics dictionary)
    """
    logger.info(
        f"Mutating population with rate={mutation_rate}, {len(mutator_dtos)} mutators"
    )

    # Instantiate mutators
    mutators = [instantiate_component(dto, component_classes) for dto in mutator_dtos]

    mutated_candidates = []
    metrics = {
        "candidates_mutated": 0,
        "total_candidates": len(population_dto.candidates),
        "mutation_rate": mutation_rate,
    }

    for candidate in population_dto.candidates:
        # Decide if mutation occurs
        if random.random() < mutation_rate and mutators:
            mutator = random.choice(mutators)
            try:
                mutated_genome = mutator.apply(candidate.genome_data, context_dto)
                mutated_candidate = CandidateDTO(
                    genome_data=mutated_genome,
                    fitness=candidate.fitness,  # Fitness will be recalculated
                    generation=candidate.generation,
                    parent_ids=[candidate.id],
                    metadata={
                        **candidate.metadata,
                        "mutated": True,
                        "mutator": mutator.name,
                    },
                )
                mutated_candidates.append(mutated_candidate)
                metrics["candidates_mutated"] += 1
            except Exception as e:
                logger.warning(f"Mutator {mutator.name} failed: {e}")
                # Keep original candidate if mutation fails
                mutated_candidates.append(candidate)
        else:
            # No mutation, keep original
            mutated_candidates.append(candidate)

    mutated_population = PopulationDTO(
        generation=population_dto.generation, candidates=mutated_candidates
    )

    metrics["mutation_percentage"] = (
        metrics["candidates_mutated"] / metrics["total_candidates"] * 100
        if metrics["total_candidates"] > 0
        else 0.0
    )

    logger.info(f"Mutation complete: {metrics}")
    return mutated_population, metrics


def crossover_population(
    population_dto: PopulationDTO,
    context_dto: ScheduleSolveContextDTO,
    component_classes: dict[str, Type[GenomeOperator]],
    crossover_rate: float,
) -> tuple[PopulationDTO, dict[str, Any]]:
    """
    Apply crossover to population based on crossover rate.
    Returns current population + crossover children.

    Args:
        population_dto: Population to apply crossover to
        context_dto: Solve context
        component_classes: Mapping of component type to class
        crossover_rate: Probability of crossover per candidate pair

    Returns:
        Tuple of (PopulationDTO with original + children, metrics dictionary)
    """
    logger.info(f"Applying crossover with rate={crossover_rate}")

    # Start with original population
    new_population = PopulationDTO(
        generation=population_dto.generation,
        candidates=population_dto.candidates.copy(),  # Copy to avoid mutation
    )

    metrics = {
        "crossover_attempts": 0,
        "crossover_successful": 0,
        "children_created": 0,
        "crossover_rate": crossover_rate,
    }

    # Pair candidates for crossover
    candidates = population_dto.candidates
    for i in range(0, len(candidates) - 1, 2):
        if i + 1 >= len(candidates):
            break

        parent1 = candidates[i]
        parent2 = candidates[i + 1]

        metrics["crossover_attempts"] += 1

        # Apply crossover based on rate
        if random.random() < crossover_rate:
            try:
                # For now, use the uniform_crossover function
                # In the future, we could look for a dedicated crossover operator
                child_genome = uniform_crossover(
                    parent1.genome_data, parent2.genome_data
                )

                # Create child candidate
                child_candidate = CandidateDTO(
                    genome_data=child_genome,
                    fitness=0.0,  # Will be scored later
                    generation=parent1.generation,
                    parent_ids=[parent1.id, parent2.id],
                    metadata={"type": "crossover_child"},
                )

                new_population.candidates.append(child_candidate)
                metrics["crossover_successful"] += 1
                metrics["children_created"] += 1

            except Exception as e:
                logger.warning(f"Crossover failed: {e}")

    logger.info(f"Crossover complete: {metrics}")
    return new_population, metrics


def uniform_crossover(parent1_genome: dict, parent2_genome: dict) -> dict:
    """
    Simple uniform crossover for schedule genomes.
    For each shift, randomly pick assignment from parent1 or parent2.
    """
    child_genome = {}

    # Get all shift IDs from both parents
    all_shift_ids = set(parent1_genome.get("assignments", {}).keys())
    all_shift_ids.update(parent2_genome.get("assignments", {}).keys())

    for shift_id in all_shift_ids:
        # Randomly pick assignment from parent1 or parent2
        if random.random() < 0.5:
            # Get from parent1
            if (
                "assignments" in parent1_genome
                and shift_id in parent1_genome["assignments"]
            ):
                child_genome[shift_id] = parent1_genome["assignments"][shift_id]
        else:
            # Get from parent2
            if (
                "assignments" in parent2_genome
                and shift_id in parent2_genome["assignments"]
            ):
                child_genome[shift_id] = parent2_genome["assignments"][shift_id]

    return {"assignments": child_genome}
