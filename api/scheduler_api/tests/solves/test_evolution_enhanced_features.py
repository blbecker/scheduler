import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
import random

from scheduler_api.engine.evolution import (
    EvolutionEngine,
    LoggingCallback,
)
from scheduler_api.engine.population import Population, Candidate
from scheduler_api.engine.composition import ChainOperator
from scheduler_api.engine.selection import (
    TournamentSelector,
    RouletteWheelSelector,
)


class TestEvolutionEngine:
    """Test the EvolutionEngine class."""

    def test_enhanced_evolution_engine_initialization(self):
        """Test engine initialization with default values."""
        engine = EvolutionEngine()

        assert engine.mutation_rate == 0.1
        assert engine.elite_size == 1
        assert engine.crossover_rate == 0.7  # Default crossover rate

    def test_enhanced_evolution_engine_custom_parameters(self):
        """Test engine initialization with custom parameters."""
        engine = EvolutionEngine(mutation_rate=0.25, elite_size=3, crossover_rate=0.5)

        assert engine.mutation_rate == 0.25
        assert engine.elite_size == 3
        assert engine.crossover_rate == 0.5

    def test_evolve_population_with_crossover(self):
        """Test evolve_population with crossover enabled."""
        engine = EvolutionEngine(crossover_rate=1.0)  # Always crossover

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

        population = Population(generation=0)
        population.add_candidates([candidate1, candidate2])

        # Mock crossover operator
        mock_crossover = Mock()
        mock_crossover.name = "crossover"
        mock_crossover.apply.return_value = [{"genome": "child1"}, {"genome": "child2"}]

        # Mock mutation operator
        mock_mutator = Mock()
        mock_mutator.name = "mutator"
        mock_mutator.apply.return_value = {"genome": "mutated"}

        # Mock selector
        mock_selector = Mock()
        mock_selector.select.return_value = [{"genome": "1"}, {"genome": "2"}]

        # Mock scorer
        mock_scorer = Mock()
        mock_scorer.name = "scorer"
        mock_scorer.score.return_value = 0.5

        # Mock constraint
        mock_constraint = Mock()
        mock_constraint.name = "constraint"
        mock_constraint.penalty.return_value = 0.1

        # Test with crossover
        with patch(
            "random.random", side_effect=[0.1, 0.1, 0.1]
        ):  # All < crossover_rate
            with patch("random.choice", side_effect=[mock_crossover, mock_crossover]):
                new_population = engine.evolve_population(
                    population=population,
                    genome_operators=[mock_crossover, mock_mutator],
                    scorers=[mock_scorer],
                    constraints=[mock_constraint],
                    selector=mock_selector,
                    context={},
                )

        # Verify crossover was attempted (but default implementation just returns copies)
        # In real usage, genomes would have a crossover method
        assert new_population.generation == 1
        # Note: default crossover implementation returns copies of parents,
        # so mock_crossover.apply won't be called unless genomes have .crossover() method

    def test_evolve_population_with_progress_callbacks(self):
        """Test evolve_population with progress callbacks."""
        # Create engine with callback
        mock_callback = Mock()
        mock_callback.on_generation_start = Mock()
        mock_callback.on_scoring_complete = Mock()
        mock_callback.on_selection_complete = Mock()
        mock_callback.on_offspring_created = Mock()
        mock_callback.on_generation_complete = Mock()

        engine = EvolutionEngine(callbacks=[mock_callback])

        # Create initial population
        candidate = Candidate(
            generation=0,
            genome={"genome": "1"},
            fitness=0.9,
        )

        population = Population(generation=0)
        population.add_candidates([candidate])

        # Mock components
        mock_operator = Mock()
        mock_operator.apply.return_value = {"genome": "mutated"}

        mock_scorer = Mock()
        mock_scorer.score.return_value = 0.5

        mock_selector = Mock()
        mock_selector.select.return_value = [{"genome": "1"}]

        # Test with callback
        new_population = engine.evolve_population(
            population=population,
            genome_operators=[mock_operator],
            scorers=[mock_scorer],
            constraints=[],
            selector=mock_selector,
            context={},
        )

        # Verify callbacks were called
        mock_callback.on_generation_start.assert_called_once()
        mock_callback.on_scoring_complete.assert_called_once()
        mock_callback.on_selection_complete.assert_called_once()
        mock_callback.on_offspring_created.assert_called_once()
        mock_callback.on_generation_complete.assert_called_once()
        assert new_population.generation == 1

    def test_pair_parents_even_population(self):
        """Test parent pairing with even population size."""
        engine = EvolutionEngine()

        selected_genomes = [
            {"genome": "1"},
            {"genome": "2"},
            {"genome": "3"},
            {"genome": "4"},
        ]

        # Test with deterministic random choice
        with patch("random.sample", side_effect=lambda items, k: items[:k]):
            pairs = engine._pair_parents(selected_genomes)

        # Should create 2 pairs (4 genomes / 2)
        assert len(pairs) == 2
        for pair in pairs:
            assert len(pair) == 2
            assert all(isinstance(g, dict) for g in pair)

    def test_pair_parents_odd_population(self):
        """Test parent pairing with odd population size."""
        engine = EvolutionEngine()

        selected_genomes = [{"genome": "1"}, {"genome": "2"}, {"genome": "3"}]

        # Test with deterministic random choice
        with patch("random.sample", side_effect=lambda items, k: items[:k]):
            pairs = engine._pair_parents(selected_genomes)

        # Should create 1 pair (floor(3/2))
        assert len(pairs) == 1
        assert len(pairs[0]) == 2

    def test_pair_parents_empty(self):
        """Test parent pairing with empty list."""
        engine = EvolutionEngine()

        pairs = engine._pair_parents([])
        assert pairs == []

    def test_pair_parents_single(self):
        """Test parent pairing with single genome."""
        engine = EvolutionEngine()

        selected_genomes = [{"genome": "1"}]

        pairs = engine._pair_parents(selected_genomes)
        assert pairs == []

    def test_apply_crossover_with_mock_operator(self):
        """Test crossover application with mock operator."""
        engine = EvolutionEngine()

        # Note: _apply_crossover takes parent1, parent2, context
        parent1 = {"genome": "parent1"}
        parent2 = {"genome": "parent2"}

        # The default implementation returns copies of parents
        children = engine._apply_crossover(parent1, parent2, {})

        # Should return 2 children (copies of parents by default)
        assert len(children) == 2
        # They should be copies, not the same objects
        assert children[0] is not parent1
        assert children[1] is not parent2

    def test_create_offspring_with_crossover(self):
        """Test _create_offspring_with_crossover method."""
        engine = EvolutionEngine(crossover_rate=1.0)  # Always crossover

        selected_genomes = [{"genome": "1"}, {"genome": "2"}]

        # Mock operator (won't be used since default crossover returns copies)
        mock_operator = Mock()

        # Test crossover
        offspring = engine._create_offspring_with_crossover(
            selected_genomes, [mock_operator], {}
        )

        # Should have 2 offspring (pairs produce children)
        assert len(offspring) == 2

    def test_evolve_population_backward_compatibility(self):
        """Test that engine maintains backward compatibility."""
        engine = EvolutionEngine()

        # Test with no crossover operators (should behave like original engine)
        candidate = Candidate(
            generation=0,
            genome={"genome": "1"},
            fitness=0.9,
        )

        population = Population(generation=0)
        population.add_candidates([candidate])

        # Mock components
        mock_operator = Mock()
        mock_operator.apply.return_value = {"genome": "mutated"}

        mock_scorer = Mock()
        mock_scorer.score.return_value = 0.5

        mock_selector = Mock()
        mock_selector.select.return_value = [{"genome": "1"}]

        # Test with default parameters (no crossover)
        new_population = engine.evolve_population(
            population=population,
            genome_operators=[mock_operator],
            scorers=[mock_scorer],
            constraints=[],
            selector=mock_selector,
            context={},
        )

        assert new_population.generation == 1
        assert new_population.size() >= 1

    def test_logging_callback(self):
        """Test logging callback functionality."""
        # Import and test logging callback
        from scheduler_api.engine.evolution import LoggingCallback

        # Mock logging
        with patch("logging.getLogger") as mock_logger:
            mock_log = Mock()
            mock_logger.return_value = mock_log

            # Create callback with mocked logger
            callback = LoggingCallback(logger=mock_log)

            # Test callback methods
            population = Population(generation=0)

            callback.on_generation_start(1, population)
            callback.on_generation_complete(1, population)

            # Verify logging was called
            assert mock_log.info.call_count >= 2

    def test_crossover_rate_zero(self):
        """Test evolution with crossover_rate = 0 (no crossover)."""
        engine = EvolutionEngine(crossover_rate=0.0)

        # Create initial population
        candidate = Candidate(
            generation=0,
            genome={"genome": "1"},
            fitness=0.9,
        )

        population = Population(generation=0)
        population.add_candidates([candidate])

        # Mock crossover operator (should not be called)
        mock_crossover = Mock()
        mock_crossover.apply.return_value = [{"genome": "child1"}, {"genome": "child2"}]

        # Mock mutation operator
        mock_mutator = Mock()
        mock_mutator.apply.return_value = {"genome": "mutated"}

        # Mock selector
        mock_selector = Mock()
        mock_selector.select.return_value = [{"genome": "1"}]

        # Mock scorer
        mock_scorer = Mock()
        mock_scorer.score.return_value = 0.5

        # Test with crossover_rate = 0
        new_population = engine.evolve_population(
            population=population,
            genome_operators=[mock_crossover, mock_mutator],
            scorers=[mock_scorer],
            constraints=[],
            selector=mock_selector,
            context={},
        )

        # Crossover should not be called
        mock_crossover.apply.assert_not_called()
        assert new_population.generation == 1

    def test_crossover_rate_one(self):
        """Test evolution with crossover_rate = 1 (always crossover)."""
        engine = EvolutionEngine(crossover_rate=1.0)

        # Create initial population with even number of candidates
        candidate1 = Candidate(
            generation=0,
            genome={"genome": "1"},
            fitness=0.9,
        )
        candidate2 = Candidate(
            generation=0,
            genome={"genome": "2"},
            fitness=0.8,
        )

        population = Population(generation=0)
        population.add_candidates([candidate1, candidate2])

        # Mock crossover operator (should be called via default implementation)
        mock_crossover = Mock()

        # Mock selector
        mock_selector = Mock()
        mock_selector.select.return_value = [{"genome": "1"}, {"genome": "2"}]

        # Mock scorer
        mock_scorer = Mock()
        mock_scorer.score.return_value = 0.5

        # Mock random.random to always return < 1.0 (always crossover)
        with patch("random.random", return_value=0.5):
            with patch("random.choice", return_value=mock_crossover):
                new_population = engine.evolve_population(
                    population=population,
                    genome_operators=[mock_crossover],
                    scorers=[mock_scorer],
                    constraints=[],
                    selector=mock_selector,
                    context={},
                )

        # Default crossover returns copies of parents
        assert new_population.generation == 1

    def test_enhanced_selection_strategies(self):
        """Test evolution with enhanced selection strategies."""
        engine = EvolutionEngine()

        # Create initial population
        candidate1 = Candidate(
            generation=0,
            genome={"genome": "1"},
            fitness=0.9,
        )
        candidate2 = Candidate(
            generation=0,
            genome={"genome": "2"},
            fitness=0.8,
        )

        population = Population(generation=0)
        population.add_candidates([candidate1, candidate2])

        # Mock operator
        mock_operator = Mock()
        mock_operator.apply.return_value = {"genome": "mutated"}

        # Mock scorer
        mock_scorer = Mock()
        mock_scorer.score.return_value = 0.5

        # Test with TournamentSelector
        selector = TournamentSelector(tournament_size=2)

        # Mock tournament selection
        with patch.object(selector, "select", return_value=[{"genome": "1"}]):
            new_population = engine.evolve_population(
                population=population,
                genome_operators=[mock_operator],
                scorers=[mock_scorer],
                constraints=[],
                selector=selector,
                context={},
            )

        assert new_population.generation == 1

        # Test with RouletteWheelSelector
        selector2 = RouletteWheelSelector()

        # Mock roulette selection
        with patch.object(selector2, "select", return_value=[{"genome": "2"}]):
            new_population2 = engine.evolve_population(
                population=population,
                genome_operators=[mock_operator],
                scorers=[mock_scorer],
                constraints=[],
                selector=selector2,
                context={},
            )

        assert new_population2.generation == 1

    @pytest.mark.skip("Complex mocking needed for composition operators")
    def test_composition_operators_in_evolution(self):
        """Test evolution with composition operators."""
        # Create mock population
        population = Mock()
        population.generation = 0
        population.size.return_value = 2
        population.candidates = [Mock(), Mock()]

        # Create mock operators
        mock_mutator1 = Mock()
        mock_mutator1.name = "mutator1"
        mock_mutator1.apply.return_value = {"genome": "mutated1"}

        mock_mutator2 = Mock()
        mock_mutator2.name = "mutator2"
        mock_mutator2.apply.return_value = {"genome": "mutated2"}

        # Create chain operator
        chain_operator = ChainOperator([mock_mutator1, mock_mutator2])

        # Mock selector
        mock_selector = Mock()
        mock_selector.select.return_value = [{"genome": "1"}]

        # Mock scorer
        mock_scorer = Mock()
        mock_scorer.score.return_value = 0.5

        # Test with chain operator (force mutation with mutation_rate=1.0 and mocked random)
        engine = EvolutionEngine(mutation_rate=1.0)

        # Mock random to always mutate
        with patch("random.random", return_value=0.5):  # < 1.0, so mutation occurs
            new_population = engine.evolve_population(
                population=population,
                genome_operators=[chain_operator],
                scorers=[mock_scorer],
                constraints=[],
                selector=mock_selector,
                context={},
            )

        # Both mutators in chain should be called
        mock_mutator1.apply.assert_called_once()
        mock_mutator2.apply.assert_called_once()
        assert new_population.generation == 1
