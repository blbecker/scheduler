"""Evolution engine for genetic algorithm."""

import random
import time
from typing import Any, Optional
from uuid import UUID
from ..interfaces import (
    GenomeOperator,
    Scorable,
    Constraint,
    Selector,
    Seeder,
    Stoppable)
from .population import Population, Candidate


class EvolutionEngine:
    """Engine that executes genetic algorithm evolution cycles."""

    def __init__(self, mutation_rate: float = 0.1, elite_size: int = 1):
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size

    def evolve_population(
        self,
        population: Population,
        genome_operators: list[GenomeOperator],
        scorers: list[Scorable],
        constraints: list[Constraint],
        selector: Selector,
        context: Any) -> Population:
        """Execute one evolution cycle on population."""
        if population.is_empty():
            return population

        # Score current population
        scored_candidates = self._score_population(
            population.candidates, scorers, constraints, context
        )

        # Use selector to choose parents for next generation
        # Convert to (genome, fitness) format for selector
        genomes_with_fitness = [
            (candidate.genome, candidate.fitness) for candidate, _ in scored_candidates
        ]

        # Select parents for next generation
        target_size = population.size()
        selected_genomes = selector.select(genomes_with_fitness, context, target_size)

        # Create new population for next generation
        new_population = Population(generation=population.generation + 1)

        # Keep elite candidates (top performers)
        elites = population.get_top_n(self.elite_size)
        for elite in elites:
            elite_candidate = Candidate(
                generation=new_population.generation,
                genome=elite.genome,
                fitness=elite.fitness,
                score_breakdown=elite.score_breakdown.copy(),
                parent_ids=[elite.id],
                metadata={"type": "elite"})
            new_population.add_candidate(elite_candidate)

        # Apply genetic operators to create offspring from selected genomes
        offspring_genomes = self._create_offspring(
            selected_genomes, genome_operators, context
        )

        # Create candidates from offspring genomes
        offspring_candidates = []
        for genome in offspring_genomes:
            candidate = self._create_candidate_from_genome(
                genome, new_population.generation, scorers, constraints, context
            )
            offspring_candidates.append(candidate)

        # Add offspring to new population
        for candidate in offspring_candidates:
            new_population.add_candidate(candidate)

        # Ensure we have enough candidates
        # If not, add some random genomes from selected parents
        while new_population.size() < target_size and selected_genomes:
            genome = random.choice(selected_genomes)
            candidate = self._create_candidate_from_genome(
                genome, new_population.generation, scorers, constraints, context
            )
            new_population.add_candidate(candidate)

        return new_population

    def _score_population(
        self,
        candidates: list[Candidate],
        scorers: list[Scorable],
        constraints: list[Constraint],
        context: Any) -> list[tuple[Candidate, float]]:
        """Score candidates and return list of (candidate, total_score)."""
        scored = []

        for candidate in candidates:
            total_score = 0.0
            score_breakdown = {}

            # Calculate scores from scorers
            for scorer in scorers:
                score = scorer.score(candidate.genome, context)
                total_score += score
                score_breakdown[scorer.name] = score

            # Apply constraint penalties
            for constraint in constraints:
                penalty = constraint.penalty(candidate.genome, context)
                total_score -= penalty
                score_breakdown[f"{constraint.name}_penalty"] = penalty

            # Update candidate with new scores
            candidate.fitness = max(0.0, total_score)  # Fitness can't be negative
            candidate.score_breakdown = score_breakdown

            scored.append((candidate, candidate.fitness))

        return scored

    def _create_offspring(
        self,
        selected_genomes: list[Any],
        genome_operators: list[GenomeOperator],
        context: Any) -> list[Any]:
        """Create offspring genomes using genetic operators."""
        if not genome_operators or not selected_genomes:
            return []

        offspring = []

        # For each selected genome, potentially create offspring
        for genome in selected_genomes:
            # Apply mutation with probability
            if random.random() < self.mutation_rate and genome_operators:
                operator = random.choice(genome_operators)
                mutated_genome = operator.apply(genome, context)
                offspring.append(mutated_genome)

            # Also keep some originals (simplified reproduction)
            if random.random() < 0.5:  # 50% chance to keep original
                offspring.append(genome.copy())

        return offspring

    def _create_candidate_from_genome(
        self,
        genome: Any,
        generation: int,
        scorers: list[Scorable],
        constraints: list[Constraint],
        context: Any) -> Candidate:
        """Create a Candidate from a single genome with scoring."""
        total_score = 0.0
        score_breakdown = {}

        # Calculate scores
        for scorer in scorers:
            score = scorer.score(genome, context)
            total_score += score
            score_breakdown[scorer.name] = score

        # Apply constraint penalties
        for constraint in constraints:
            penalty = constraint.penalty(genome, context)
            total_score -= penalty
            score_breakdown[f"{constraint.name}_penalty"] = penalty

        # Create candidate
        return Candidate(
            generation=generation,
            genome=genome,
            fitness=max(0.0, total_score),
            score_breakdown=score_breakdown,
            metadata={"created_by": "evolution"})
