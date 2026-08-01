"""Enhanced selection strategy implementations."""

import random
import math
from typing import TypeVar, Generic
from ..interfaces import Selector

# Type variables
T = TypeVar("T")  # Context type
G = TypeVar("G")  # Genome type


class TournamentSelector(Selector[G, T]):
    """K-way tournament selection."""

    def __init__(self, tournament_size: int = 3, name: str = "tournament_selector"):
        self.tournament_size = tournament_size
        self.name = name

    def select(
        self, population: list[tuple[G, float]], context: T, count: int
    ) -> list[G]:
        """Select genomes using tournament selection."""
        if not population:
            return []

        selected = []
        for _ in range(count):
            # Randomly sample tournament participants
            tournament = random.sample(
                population, min(self.tournament_size, len(population))
            )
            # Select winner (highest fitness)
            winner = max(tournament, key=lambda x: x[1])
            selected.append(winner[0])

        return selected

    def __str__(self) -> str:
        return f"TournamentSelector[size={self.tournament_size}]"


class RouletteWheelSelector(Selector[G, T]):
    """Fitness-proportionate selection (roulette wheel)."""

    def __init__(self, name: str = "roulette_wheel_selector"):
        self.name = name

    def select(
        self, population: list[tuple[G, float]], context: T, count: int
    ) -> list[G]:
        """Select genomes using roulette wheel selection."""
        if not population:
            return []

        # Ensure all fitness values are non-negative
        min_fitness = min(f for _, f in population)
        offset = abs(min_fitness) + 0.01 if min_fitness < 0 else 0

        # Calculate selection probabilities
        total_fitness = sum(f + offset for _, f in population)

        # Handle edge case where all fitness values are zero
        if total_fitness <= 0:
            # Equal probability for all
            return random.choices([g for g, _ in population], k=count)

        probabilities = [(f + offset) / total_fitness for _, f in population]

        # Roulette wheel selection
        selected = []
        for _ in range(count):
            rand = random.random()
            cumulative = 0.0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if rand <= cumulative:
                    selected.append(population[i][0])
                    break

        return selected

    def __str__(self) -> str:
        return "RouletteWheelSelector"


class RankingSelector(Selector[G, T]):
    """Rank-based selection with linear or exponential ranking."""

    def __init__(
        self,
        selection_pressure: float = 1.5,
        ranking_method: str = "linear",
        name: str = "ranking_selector",
    ):
        """
        Args:
            selection_pressure: Higher values favor top ranks (1.0 < pressure <= 2.0)
            ranking_method: 'linear' or 'exponential'
        """
        self.selection_pressure = selection_pressure
        self.ranking_method = ranking_method
        self.name = name

        if ranking_method not in ["linear", "exponential"]:
            raise ValueError(f"Invalid ranking method: {ranking_method}")

    def select(
        self, population: list[tuple[G, float]], context: T, count: int
    ) -> list[G]:
        """Select genomes using rank-based selection."""
        if not population:
            return []

        # Sort population by fitness (descending)
        sorted_population = sorted(population, key=lambda x: x[1], reverse=True)
        n = len(sorted_population)

        # Calculate rank probabilities
        if self.ranking_method == "linear":
            probabilities = self._linear_ranking_probabilities(n)
        else:  # exponential
            probabilities = self._exponential_ranking_probabilities(n)

        # Select based on rank probabilities
        selected = []
        for _ in range(count):
            rank = random.choices(range(n), weights=probabilities)[0]
            selected.append(sorted_population[rank][0])

        return selected

    def _linear_ranking_probabilities(self, n: int) -> list[float]:
        """Calculate linear ranking probabilities."""
        probabilities = []
        for i in range(n):
            rank = i + 1  # 1-based rank (1 = best)
            probability = (2 - self.selection_pressure) / n + 2 * (
                self.selection_pressure - 1
            ) * (n - rank) / (n * (n - 1))
            probabilities.append(probability)
        return probabilities

    def _exponential_ranking_probabilities(self, n: int) -> list[float]:
        """Calculate exponential ranking probabilities."""
        probabilities = []
        total = 0.0
        for i in range(n):
            rank = i + 1  # 1-based rank (1 = best)
            probability = math.exp(-self.selection_pressure * (rank - 1) / n)
            probabilities.append(probability)
            total += probability

        # Normalize
        return [p / total for p in probabilities]

    def __str__(self) -> str:
        return f"RankingSelector[{self.ranking_method}, pressure={self.selection_pressure}]"


class CompositeSelector(Selector[G, T]):
    """Combine multiple selection strategies."""

    def __init__(
        self,
        selectors: list[tuple[Selector[G, T], float]],
        name: str = "composite_selector",
    ):
        """
        Args:
            selectors: List of (selector, weight) pairs
        """
        # Normalize weights
        total_weight = sum(weight for _, weight in selectors)
        self.selectors = [(sel, weight / total_weight) for sel, weight in selectors]
        self.name = name

    def select(
        self, population: list[tuple[G, float]], context: T, count: int
    ) -> list[G]:
        """Select genomes using composite strategy."""
        if not population:
            return []

        selected = []
        for _ in range(count):
            # Weighted random selection of selector
            rand = random.random()
            cumulative = 0.0
            for selector, weight in self.selectors:
                cumulative += weight
                if rand <= cumulative:
                    # Use selected selector to pick one genome
                    genome = selector.select(population, context, 1)
                    if genome:
                        selected.append(genome[0])
                    break

        return selected

    def __str__(self) -> str:
        return f"CompositeSelector[{len(self.selectors)} selectors]"
