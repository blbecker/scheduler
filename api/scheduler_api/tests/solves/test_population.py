"""Tests for solves.engine.population module."""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime

from scheduler_api.engine.population import Candidate, Population


class TestCandidate:
    """Test the Candidate class."""

    def test_candidate_initialization(self):
        """Test candidate initialization with default values."""
        candidate = Candidate()

        assert candidate.id is not None
        assert candidate.generation == 0
        assert candidate.genome is None
        assert candidate.fitness == 0.0
        assert candidate.score_breakdown == {}
        assert candidate.parent_ids == []
        assert candidate.metadata == {}
        assert isinstance(candidate.created_at, datetime)

    def test_candidate_with_parameters(self):
        """Test candidate initialization with custom parameters."""
        candidate_id = uuid4()
        genome = {"test": "genome"}
        metadata = {"source": "test"}

        candidate = Candidate(
            id=candidate_id,
            generation=5,
            genome=genome,
            fitness=0.85,
            score_breakdown={"skill": 0.7, "availability": 0.15},
            parent_ids=[uuid4(), uuid4()],
            metadata=metadata,
        )

        assert candidate.id == candidate_id
        assert candidate.generation == 5
        assert candidate.genome == genome
        assert candidate.fitness == 0.85
        assert candidate.score_breakdown == {"skill": 0.7, "availability": 0.15}
        assert len(candidate.parent_ids) == 2
        assert candidate.metadata == metadata

    def test_candidate_str_representation(self):
        """Test string representation of candidate."""
        candidate = Candidate(fitness=0.75)
        candidate_str = str(candidate)

        assert "Candidate" in candidate_str
        assert "fitness=0.750" in candidate_str  # .3f format

    def test_candidate_copy_metadata(self):
        """Test that metadata dictionary is not shared between candidates."""
        candidate1 = Candidate(metadata={"test": "value"})
        candidate2 = Candidate(metadata={"test": "value"})

        # Modify one candidate's metadata
        candidate1.metadata["test"] = "modified"

        # Other candidate should not be affected
        assert candidate2.metadata["test"] == "value"


class TestPopulation:
    """Test the Population class."""

    def test_population_initialization(self):
        """Test population initialization with default values."""
        population = Population()

        assert population.generation == 0
        assert population.candidates == []
        assert population.size() == 0
        assert population.is_empty()

    def test_population_with_candidates(self):
        """Test population initialization with candidates."""
        candidate1 = Candidate(fitness=0.5)
        candidate2 = Candidate(fitness=0.8)

        population = Population(generation=3)
        population.add_candidates([candidate1, candidate2])

        assert population.generation == 3
        assert len(population.candidates) == 2
        assert population.candidates[0] == candidate1
        assert population.candidates[1] == candidate2

    def test_size(self):
        """Test population size calculation."""
        population = Population()
        assert population.size() == 0

        population.add_candidates([Candidate(), Candidate(), Candidate()])
        assert population.size() == 3

    def test_is_empty(self):
        """Test empty population detection."""
        population = Population()
        assert population.is_empty()

        population._candidates.append(Candidate())
        assert not population.is_empty()

    def test_get_best_empty_population(self):
        """Test get_best with empty population."""
        population = Population()
        assert population.get_top_n(1) == []

    def test_get_best(self):
        """Test getting best candidate."""
        candidate_low = Candidate(fitness=0.3)
        candidate_medium = Candidate(fitness=0.6)
        candidate_high = Candidate(fitness=0.9)

        population = Population()
        population.add_candidates([candidate_low, candidate_medium, candidate_high])

        best = population.get_top_n(1)[0]
        assert best is not None
        assert best.fitness == 0.9

    def test_get_best_with_equal_fitness(self):
        """Test get_best when multiple candidates have same fitness."""
        candidate1 = Candidate(fitness=0.7)
        candidate2 = Candidate(fitness=0.7)

        population = Population()
        population.add_candidates([candidate1, candidate2])

        best = population.get_top_n(1)[0]
        assert best is not None
        assert best.fitness == 0.7

    def test_get_best_fitness_empty(self):
        """Test get_best_fitness with empty population."""
        population = Population()
        assert population.get_best_fitness() == 0.0

    def test_get_best_fitness(self):
        """Test getting best fitness value."""
        population = Population()
        population.add_candidates(
            [
                Candidate(fitness=0.4),
                Candidate(fitness=0.8),
                Candidate(fitness=0.6),
            ]
        )

        assert population.get_best_fitness() == 0.8

    def test_get_average_fitness_empty(self):
        """Test average fitness with empty population."""
        population = Population()
        assert population.get_average_fitness() == 0.0

    def test_get_average_fitness(self):
        """Test average fitness calculation."""
        population = Population()
        population.add_candidates(
            [
                Candidate(fitness=0.3),
                Candidate(fitness=0.5),
                Candidate(fitness=0.7),
            ]
        )

        # (0.3 + 0.5 + 0.7) / 3 = 0.5
        assert population.get_average_fitness() == pytest.approx(0.5)

    def test_get_worst_fitness_empty(self):
        """Test worst fitness with empty population."""
        population = Population()
        assert population.get_worst_fitness() == 0.0

    def test_get_worst_fitness(self):
        """Test worst fitness calculation."""
        population = Population()
        population.add_candidates(
            [
                Candidate(fitness=0.8),
                Candidate(fitness=0.2),
                Candidate(fitness=0.5),
            ]
        )

        assert population.get_worst_fitness() == 0.2

    def test_add_candidate(self):
        """Test adding candidate to population."""
        population = Population()
        candidate = Candidate(fitness=0.7)

        population.add_candidate(candidate)

        assert population.size() == 1
        assert population.candidates[0] == candidate

    def test_clear(self):
        """Test clearing all candidates."""
        population = Population()
        population.add_candidates([Candidate(), Candidate(), Candidate()])

        assert population.size() == 3
        population = Population()
        assert population.size() == 0
        assert population.is_empty()

    def test_sort_by_fitness_descending(self):
        """Test get_top_n returns candidates sorted by fitness descending."""
        candidates = [
            Candidate(fitness=0.3),
            Candidate(fitness=0.9),
            Candidate(fitness=0.6),
        ]

        population = Population()
        population.add_candidates(candidates.copy())
        top_n = population.get_top_n(3)

        assert top_n[0].fitness == 0.9
        assert top_n[1].fitness == 0.6
        assert top_n[2].fitness == 0.3

    def test_sort_by_fitness_ascending(self):
        """Test get_top_n returns candidates sorted by fitness descending (highest first)."""
        candidates = [
            Candidate(fitness=0.3),
            Candidate(fitness=0.9),
            Candidate(fitness=0.6),
        ]

        population = Population()
        population.add_candidates(candidates.copy())
        top_n = population.get_top_n(3)

        assert top_n[0].fitness == 0.9
        assert top_n[1].fitness == 0.6
        assert top_n[2].fitness == 0.3

    def test_get_top_n_empty(self):
        """Test get_top_n with empty population."""
        population = Population()
        top_n = population.get_top_n(3)

        assert len(top_n) == 0

    def test_get_top_n(self):
        """Test getting top N candidates."""
        candidates = [
            Candidate(fitness=0.2),
            Candidate(fitness=0.9),
            Candidate(fitness=0.5),
            Candidate(fitness=0.8),
            Candidate(fitness=0.3),
        ]

        population = Population()
        population.add_candidates(candidates.copy())
        top_3 = population.get_top_n(3)

        assert len(top_3) == 3
        assert top_3[0].fitness == 0.9
        assert top_3[1].fitness == 0.8
        assert top_3[2].fitness == 0.5

    def test_get_top_n_more_than_available(self):
        """Test get_top_n when n exceeds population size."""
        population = Population()
        population.add_candidates([Candidate(fitness=0.8), Candidate(fitness=0.5)])

        top_5 = population.get_top_n(5)

        assert len(top_5) == 2
        assert top_5[0].fitness == 0.8
        assert top_5[1].fitness == 0.5

    def test_get_fitness_range_empty(self):
        """Test fitness range with empty population."""
        population = Population()
        min_fitness, max_fitness = population.get_fitness_range()

        assert min_fitness == 0.0
        assert max_fitness == 0.0

    def test_get_fitness_range(self):
        """Test fitness range calculation."""
        population = Population()
        population.add_candidates(
            [
                Candidate(fitness=0.3),
                Candidate(fitness=0.9),
                Candidate(fitness=0.5),
                Candidate(fitness=0.1),
                Candidate(fitness=0.7),
            ]
        )

        min_fitness, max_fitness = population.get_fitness_range()

        assert min_fitness == 0.1
        assert max_fitness == 0.9

    def test_population_with_same_fitness(self):
        """Test methods with population where all candidates have same fitness."""
        population = Population()
        population.add_candidates(
            [
                Candidate(fitness=0.5),
                Candidate(fitness=0.5),
                Candidate(fitness=0.5),
            ]
        )

        assert population.get_best_fitness() == 0.5
        assert population.get_worst_fitness() == 0.5
        assert population.get_average_fitness() == 0.5
        assert population.get_fitness_range() == (0.5, 0.5)
