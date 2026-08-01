"""Evolution engine for genetic algorithm with crossover support and progress callbacks."""

import random
from typing import Any, Generic, TypeVar, Optional
from copy import deepcopy

from .interfaces import (
    GenomeOperator,
    Scorable,
    Constraint,
    Selector,
    Seeder,
    Stoppable,
)
from .population import Population, Candidate
from .callbacks import EvolutionCallback, LoggingCallback

G = TypeVar("G")  # Genome type parameter
T = TypeVar("T")  # Context type parameter


class EvolutionEngine(Generic[G, T]):
    """Generic evolution engine for genetic algorithm with crossover support."""

    def __init__(
        self,
        mutation_rate: float = 0.1,
        elite_size: int = 1,
        crossover_rate: float = 0.7,
        callbacks: Optional[list[EvolutionCallback[Population[G]]]] = None,
    ):
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.crossover_rate = crossover_rate
        self.callbacks: list[EvolutionCallback[Population[G]]] = callbacks or []

    def evolve_population(
        self,
        population: Population[G],
        genome_operators: list[GenomeOperator[G, T]],
        scorers: list[Scorable[G, T]],
        constraints: list[Constraint[G, T]],
        selector: Selector[G, T],
        context: T,
    ) -> Population[G]:
        """Execute one evolution cycle on population with crossover and progress callbacks."""
        if population.is_empty():
            return population

        # Notify generation start
        for callback in self.callbacks:
            callback.on_generation_start(population.generation + 1, population)

        # Score current population
        scored_candidates = self._score_population(
            population.candidates, scorers, constraints, context
        )

        # Notify scoring complete
        for callback in self.callbacks:
            callback.on_scoring_complete(population)

        # Convert to (genome, fitness) format for selector
        genomes_with_fitness = [
            (candidate.genome, candidate.fitness) for candidate, _ in scored_candidates
        ]

        # Select parents for next generation
        target_size = population.size()
        selected_genomes = selector.select(genomes_with_fitness, context, target_size)

        # Notify selection complete
        for callback in self.callbacks:
            callback.on_selection_complete(selected_genomes, context)

        # Create new population for next generation
        new_population = Population[G](generation=population.generation + 1)

        # Keep elite candidates (top performers)
        elites = population.get_top_n(self.elite_size)
        for elite in elites:
            elite_candidate = Candidate[G](
                generation=new_population.generation,
                genome=elite.genome,
                fitness=elite.fitness,
                score_breakdown=elite.score_breakdown.copy(),
                parent_ids=[elite.id],
                metadata={"type": "elite"},
            )
            new_population.add_candidate(elite_candidate)

        # Create offspring with crossover and mutation
        offspring_genomes = self._create_offspring_with_crossover(
            selected_genomes, genome_operators, context
        )

        # Notify offspring created
        for callback in self.callbacks:
            callback.on_offspring_created(offspring_genomes)

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

        # Notify generation complete
        for callback in self.callbacks:
            callback.on_generation_complete(new_population.generation, new_population)

        return new_population

    def _score_population(
        self,
        candidates: list[Candidate[G]],
        scorers: list[Scorable[G, T]],
        constraints: list[Constraint[G, T]],
        context: T,
    ) -> list[tuple[Candidate[G], float]]:
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
        selected_genomes: list[G],
        genome_operators: list[GenomeOperator[G, T]],
        context: T,
    ) -> list[G]:
        """Create offspring genomes (backward compatibility wrapper)."""
        return self._create_offspring_with_crossover(
            selected_genomes, genome_operators, context
        )

    def _create_offspring_with_crossover(
        self,
        selected_genomes: list[G],
        genome_operators: list[GenomeOperator[G, T]],
        context: T,
    ) -> list[G]:
        """Create offspring genomes with crossover and mutation."""
        if not selected_genomes:
            return []

        offspring = []

        # Pair parents for crossover
        parent_pairs = self._pair_parents(selected_genomes)

        # Handle single genome case (no pairs)
        if not parent_pairs and selected_genomes:
            # With single genome, just copy it
            for genome in selected_genomes:
                if random.random() < self.mutation_rate and genome_operators:
                    operator = random.choice(genome_operators)
                    mutated = operator.apply(self._copy_genome(genome), context)
                    offspring.append(mutated)
                else:
                    offspring.append(self._copy_genome(genome))
            return offspring

        for parent1, parent2 in parent_pairs:
            # Apply crossover with probability
            if random.random() < self.crossover_rate:
                children = self._apply_crossover(parent1, parent2, context)
                offspring.extend(children)
            else:
                # No crossover, just copy parents
                offspring.append(self._copy_genome(parent1))
                offspring.append(self._copy_genome(parent2))

        # Apply mutation to offspring
        mutated_offspring = []
        for genome in offspring:
            if random.random() < self.mutation_rate and genome_operators:
                operator = random.choice(genome_operators)
                mutated_genome = operator.apply(genome, context)
                mutated_offspring.append(mutated_genome)
            else:
                mutated_offspring.append(self._copy_genome(genome))

        return mutated_offspring

    def _pair_parents(self, genomes: list[G]) -> list[tuple[G, G]]:
        """Pair genomes for crossover."""
        if len(genomes) < 2:
            return []

        # Shuffle and pair
        shuffled = random.sample(genomes, len(genomes))
        pairs = []
        for i in range(0, len(shuffled) - 1, 2):
            pairs.append((shuffled[i], shuffled[i + 1]))

        return pairs

    def _apply_crossover(self, parent1: G, parent2: G, context: T) -> list[G]:
        """Apply crossover operation to create children."""
        # Default implementation: try to use genome's crossover method if it exists
        try:
            # Try to use genome's crossover method if it exists
            if hasattr(parent1, "crossover") and callable(parent1.crossover):
                children = parent1.crossover(parent2, context)
                if isinstance(children, list):
                    return children
        except (AttributeError, TypeError):
            pass

        # Fallback: return copies of parents (no crossover implemented)
        return [self._copy_genome(parent1), self._copy_genome(parent2)]

    def _copy_genome(self, genome: G) -> G:
        """Create a copy of the genome."""
        try:
            # Try to use genome's copy method if it exists
            return genome.copy()
        except AttributeError:
            # Fallback to deepcopy
            return deepcopy(genome)

    def _create_candidate_from_genome(
        self,
        genome: G,
        generation: int,
        scorers: list[Scorable[G, T]],
        constraints: list[Constraint[G, T]],
        context: T,
    ) -> Candidate[G]:
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
        return Candidate[G](
            generation=generation,
            genome=genome,
            fitness=max(0.0, total_score),
            score_breakdown=score_breakdown,
            metadata={"created_by": "evolution"},
        )
