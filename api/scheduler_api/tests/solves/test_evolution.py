"""Tests for solves.engine.evolution module."""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
import random

from scheduler_api.solves.engine.evolution import EvolutionEngine
from scheduler_api.solves.engine.population import Population, Candidate


class TestEvolutionEngine:
    """Test the EvolutionEngine class."""

    def test_evolution_engine_initialization(self):
        """Test engine initialization with default values."""
        engine = EvolutionEngine()

        assert engine.mutation_rate == 0.1
        assert engine.elite_size == 1

    def test_evolution_engine_custom_parameters(self):
        """Test engine initialization with custom parameters."""
        engine = EvolutionEngine(mutation_rate=0.25, elite_size=3)

        assert engine.mutation_rate == 0.25
        assert engine.elite_size == 3

    def test_evolve_population_empty(self):
        """Test evolve_population with empty population."""
        engine = EvolutionEngine()
        population = Population()

        result = engine.evolve_population(
            population=population,
            genome_operators=[],
            scorers=[],
            constraints=[],
            selector=Mock(),
            context={},
        )

        assert result is population  # Should return same population

    def test_score_population_with_scorers_only(self):
        """Test scoring with only scorers (no constraints)."""
        engine = EvolutionEngine()

        # Create mock scorers
        mock_scorer1 = Mock()
        mock_scorer1.name = "skill_scorer"
        mock_scorer1.score.return_value = 0.6

        mock_scorer2 = Mock()
        mock_scorer2.name = "availability_scorer"
        mock_scorer2.score.return_value = 0.3

        mock_genome = {"assignments": {}}
        candidate = Candidate(genome=mock_genome, fitness=0.0)

        # Mock constraints list is empty
        constraints = []

        scored_candidates = engine._score_population(
            candidates=[candidate],
            scorers=[mock_scorer1, mock_scorer2],
            constraints=constraints,
            context={},
        )

        assert len(scored_candidates) == 1
        candidate_result, total_score = scored_candidates[0]

        # Total score should be 0.6 + 0.3 = 0.9
        assert total_score == pytest.approx(0.9)
        assert candidate_result.fitness == pytest.approx(0.9)
        assert candidate_result.score_breakdown == {
            "skill_scorer": 0.6,
            "availability_scorer": 0.3,
        }

        mock_scorer1.score.assert_called_once_with(mock_genome, {})
        mock_scorer2.score.assert_called_once_with(mock_genome, {})

    def test_score_population_with_constraints(self):
        """Test scoring with constraints that add penalties."""
        engine = EvolutionEngine()

        # Create mock scorer
        mock_scorer = Mock()
        mock_scorer.name = "skill_scorer"
        mock_scorer.score.return_value = 0.8

        # Create mock constraint with penalty
        mock_constraint = Mock()
        mock_constraint.name = "no_double_booking"
        mock_constraint.penalty.return_value = 0.3

        mock_genome = {"assignments": {}}
        candidate = Candidate(genome=mock_genome, fitness=0.0)

        scored_candidates = engine._score_population(
            candidates=[candidate],
            scorers=[mock_scorer],
            constraints=[mock_constraint],
            context={},
        )

        candidate_result, total_score = scored_candidates[0]

        # Total score should be 0.8 - 0.3 = 0.5
        assert total_score == 0.5
        assert candidate_result.fitness == 0.5
        assert candidate_result.score_breakdown == {
            "skill_scorer": 0.8,
            "no_double_booking_penalty": 0.3,
        }

    def test_score_population_negative_fitness_clamped(self):
        """Test that negative total scores are clamped to 0."""
        engine = EvolutionEngine()

        # Create mock scorer with low score
        mock_scorer = Mock()
        mock_scorer.name = "skill_scorer"
        mock_scorer.score.return_value = 0.2

        # Create mock constraint with high penalty
        mock_constraint = Mock()
        mock_constraint.name = "constraint"
        mock_constraint.penalty.return_value = 0.5

        mock_genome = {"assignments": {}}
        candidate = Candidate(genome=mock_genome, fitness=0.0)

        scored_candidates = engine._score_population(
            candidates=[candidate],
            scorers=[mock_scorer],
            constraints=[mock_constraint],
            context={},
        )

        candidate_result, total_score = scored_candidates[0]

        # 0.2 - 0.5 = -0.3, should be clamped to 0
        assert total_score == 0.0
        assert candidate_result.fitness == 0.0

    def test_create_offspring_no_operators(self):
        """Test _create_offspring with no genome operators."""
        engine = EvolutionEngine()

        selected_genomes = [{"genome": "test1"}, {"genome": "test2"}]
        offspring = engine._create_offspring(selected_genomes, [], {})

        assert offspring == []

    def test_create_offspring_no_genomes(self):
        """Test _create_offspring with no selected genomes."""
        engine = EvolutionEngine()

        mock_operator = Mock()
        mock_operator.name = "mutator"
        mock_operator.apply.return_value = {"mutated": True}

        offspring = engine._create_offspring([], [mock_operator], {})

        assert offspring == []
        mock_operator.apply.assert_not_called()

    def test_create_offspring_with_mutation(self):
        """Test _create_offspring with mutation."""
        engine = EvolutionEngine(mutation_rate=1.0)  # Always mutate

        mock_operator = Mock()
        mock_operator.name = "mutator"
        mock_operator.apply.return_value = {"mutated": True}

        selected_genomes = [{"genome": "test"}]

        # Patch random.choice to return our operator
        with patch("random.choice", return_value=mock_operator):
            offspring = engine._create_offspring(selected_genomes, [mock_operator], {})

        # Should have mutated genome and possibly original (50% chance)
        assert len(offspring) >= 1
        mock_operator.apply.assert_called_once_with({"genome": "test"}, {})

    def test_create_candidate_from_genome(self):
        """Test _create_candidate_from_genome."""
        engine = EvolutionEngine()

        # Create mock scorer and constraint
        mock_scorer = Mock()
        mock_scorer.name = "scorer"
        mock_scorer.score.return_value = 0.7

        mock_constraint = Mock()
        mock_constraint.name = "constraint"
        mock_constraint.penalty.return_value = 0.2

        mock_genome = {"test": "genome"}
        context = {"template_id": uuid4()}

        candidate = engine._create_candidate_from_genome(
            genome=mock_genome,
            generation=5,
            scorers=[mock_scorer],
            constraints=[mock_constraint],
            context=context,
        )

        assert candidate.generation == 5
        assert candidate.genome == mock_genome
        assert candidate.fitness == pytest.approx(0.5)  # 0.7 - 0.2
        assert candidate.score_breakdown == {"scorer": 0.7, "constraint_penalty": 0.2}
        assert candidate.metadata == {"created_by": "evolution"}

        mock_scorer.score.assert_called_once_with(mock_genome, context)
        mock_constraint.penalty.assert_called_once_with(mock_genome, context)

    def test_full_evolve_population_cycle(self):
        """Test complete evolve_population cycle."""
        engine = EvolutionEngine(mutation_rate=0.5, elite_size=2)

        # Create initial population with candidates
        candidate1 = Candidate(
            generation=0,
            genome={"genome": "1"},
            fitness=0.9,
            score_breakdown={"scorer": 0.9},
            metadata={"type": "initial"},
        )
        candidate2 = Candidate(
            generation=0,
            genome={"genome": "2"},
            fitness=0.8,
            score_breakdown={"scorer": 0.8},
            metadata={"type": "initial"},
        )
        candidate3 = Candidate(
            generation=0,
            genome={"genome": "3"},
            fitness=0.7,
            score_breakdown={"scorer": 0.7},
            metadata={"type": "initial"},
        )

        population = Population(
            generation=0, candidates=[candidate1, candidate2, candidate3]
        )

        # Mock components
        mock_operator = Mock()
        mock_operator.name = "mutator"
        mock_operator.apply.return_value = {"genome": "mutated"}

        mock_scorer = Mock()
        mock_scorer.name = "scorer"
        mock_scorer.score.return_value = 0.5

        mock_constraint = Mock()
        mock_constraint.name = "constraint"
        mock_constraint.penalty.return_value = 0.1

        mock_selector = Mock()
        mock_selector.name = "selector"
        mock_selector.select.return_value = [
            {"genome": "1"},
            {"genome": "2"},
            {"genome": "3"},
        ]

        context = {"test": "context"}

        # Mock random functions for predictable behavior
        with patch("random.random", return_value=0.6):  # > mutation_rate, no mutation
            with patch("random.choice", side_effect=[mock_operator, {"genome": "1"}]):
                new_population = engine.evolve_population(
                    population=population,
                    genome_operators=[mock_operator],
                    scorers=[mock_scorer],
                    constraints=[mock_constraint],
                    selector=mock_selector,
                    context=context,
                )

        # Verify results
        assert new_population.generation == 1
        assert (
            new_population.size() >= 3
        )  # Should have at least elites + some offspring

        # Check that elite candidates were preserved
        elite_candidates = [
            c for c in new_population.candidates if c.metadata.get("type") == "elite"
        ]
        assert len(elite_candidates) == 2  # elite_size

        # Check selector was called correctly
        mock_selector.select.assert_called_once()
        call_args = mock_selector.select.call_args
        assert len(call_args[0][0]) == 3  # genomes_with_fitness for 3 candidates
        assert call_args[0][1] == context
        assert call_args[0][2] == 3  # target_size = population.size()

    def test_evolve_population_ensure_minimum_size(self):
        """Test that evolve_population ensures minimum population size."""
        engine = EvolutionEngine(mutation_rate=0.0, elite_size=1)  # No mutation

        # Create small population
        candidate = Candidate(
            generation=0, genome={"genome": "1"}, fitness=0.9, score_breakdown={}
        )

        population = Population(generation=0, candidates=[candidate])

        # Mock selector to return empty list (simulating selection failure)
        mock_selector = Mock()
        mock_selector.select.return_value = []

        # Mock scorer and constraint
        mock_scorer = Mock()
        mock_scorer.name = "scorer"
        mock_scorer.score.return_value = 0.5

        mock_constraint = Mock()
        mock_constraint.name = "constraint"
        mock_constraint.penalty.return_value = 0.0

        # Mock random.choice to return the original genome when needed
        with patch("random.random", return_value=0.7):  # > 0.5, keep original
            with patch("random.choice", return_value={"genome": "1"}):
                new_population = engine.evolve_population(
                    population=population,
                    genome_operators=[Mock()],
                    scorers=[mock_scorer],
                    constraints=[mock_constraint],
                    selector=mock_selector,
                    context={},
                )

        # Population should have at least 1 candidate
        assert new_population.size() >= 1
        assert new_population.generation == 1

    def test_score_population_multiple_candidates(self):
        """Test scoring multiple candidates."""
        engine = EvolutionEngine()

        # Create mock scorer with different scores for different genomes
        mock_scorer = Mock()
        mock_scorer.name = "scorer"
        mock_scorer.score.side_effect = lambda genome, context: {
            "genome1": 0.8,
            "genome2": 0.6,
            "genome3": 0.9,
        }[genome]

        # Create candidates with different genomes
        candidates = [
            Candidate(genome="genome1", fitness=0.0),
            Candidate(genome="genome2", fitness=0.0),
            Candidate(genome="genome3", fitness=0.0),
        ]

        scored_candidates = engine._score_population(
            candidates=candidates, scorers=[mock_scorer], constraints=[], context={}
        )

        assert len(scored_candidates) == 3

        # Check scores match expected values
        scores = [score for _, score in scored_candidates]
        assert 0.8 in scores
        assert 0.6 in scores
        assert 0.9 in scores

        # Check fitness updated on candidates
        for candidate, score in scored_candidates:
            assert candidate.fitness == score
            assert candidate.score_breakdown == {"scorer": score}

    def test_evolution_engine_edge_cases(self):
        """Test edge cases for evolution engine."""
        engine = EvolutionEngine(mutation_rate=0.0, elite_size=0)

        # Test with elite_size = 0
        candidate = Candidate(fitness=0.8)
        population = Population(candidates=[candidate])

        # Mock simple components
        mock_selector = Mock()
        mock_selector.select.return_value = [{"genome": "test"}]

        mock_scorer = Mock()
        mock_scorer.name = "scorer"
        mock_scorer.score.return_value = 0.5

        new_population = engine.evolve_population(
            population=population,
            genome_operators=[],
            scorers=[mock_scorer],
            constraints=[],
            selector=mock_selector,
            context={},
        )

        assert new_population.generation == 1
        # No elites, but should have offspring from selector

    def test_elite_candidates_preservation(self):
        """Test that elite candidates are preserved with correct metadata."""
        engine = EvolutionEngine(mutation_rate=0.0, elite_size=2)

        # Create population with candidates
        candidates = [
            Candidate(id=uuid4(), generation=0, fitness=0.9, genome={"g": "1"}),
            Candidate(id=uuid4(), generation=0, fitness=0.8, genome={"g": "2"}),
            Candidate(id=uuid4(), generation=0, fitness=0.7, genome={"g": "3"}),
            Candidate(id=uuid4(), generation=0, fitness=0.6, genome={"g": "4"}),
        ]

        population = Population(generation=0, candidates=candidates)

        # Mock selector to return some genomes
        mock_selector = Mock()
        mock_selector.select.return_value = [{"g": "1"}, {"g": "2"}]

        mock_scorer = Mock()
        mock_scorer.name = "scorer"
        mock_scorer.score.return_value = 0.5

        new_population = engine.evolve_population(
            population=population,
            genome_operators=[],
            scorers=[mock_scorer],
            constraints=[],
            selector=mock_selector,
            context={},
        )

        # Find elite candidates in new population
        elite_candidates = [
            c for c in new_population.candidates if c.metadata.get("type") == "elite"
        ]

        assert len(elite_candidates) == 2

        # Elites should have parent_ids referencing original candidates
        for elite in elite_candidates:
            assert len(elite.parent_ids) == 1
            assert elite.generation == 1  # New generation
            assert elite.metadata["type"] == "elite"
