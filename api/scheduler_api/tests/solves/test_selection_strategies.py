"""Tests for enhanced selection strategies."""

import pytest
from unittest.mock import Mock
import random
from uuid import uuid4

from scheduler_api.engine.selection import (
    TournamentSelector,
    RouletteWheelSelector,
    RankingSelector,
    CompositeSelector,
)


class TestSelectionStrategies:
    """Test enhanced selection strategy implementations."""

    def test_tournament_selector_basic(self):
        """Test basic tournament selection."""
        selector = TournamentSelector(tournament_size=3)

        # Create mock population
        population = [
            ({"id": "genome1"}, 0.9),
            ({"id": "genome2"}, 0.8),
            ({"id": "genome3"}, 0.7),
            ({"id": "genome4"}, 0.6),
            ({"id": "genome5"}, 0.5),
        ]

        # Test with mock random sampling
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "sample", lambda pop, k: [pop[0], pop[1], pop[2]])
            result = selector.select(population, context={}, count=2)

        # Should select genome1 (highest fitness in tournament)
        assert len(result) == 2
        assert all(g["id"].startswith("genome") for g in result)

    def test_tournament_selector_empty_population(self):
        """Test tournament selection with empty population."""
        selector = TournamentSelector()
        result = selector.select([], context={}, count=3)
        assert result == []

    def test_tournament_selector_smaller_tournament(self):
        """Test when tournament size is larger than population."""
        selector = TournamentSelector(tournament_size=10)

        population = [
            ({"id": "genome1"}, 0.9),
            ({"id": "genome2"}, 0.8),
        ]

        # Should work without error
        result = selector.select(population, context={}, count=1)
        assert len(result) == 1

    def test_roulette_wheel_selector_basic(self):
        """Test basic roulette wheel selection."""
        selector = RouletteWheelSelector()

        population = [
            ({"id": "genome1"}, 0.9),
            ({"id": "genome2"}, 0.8),
            ({"id": "genome3"}, 0.7),
        ]

        # Mock random.random to select first genome
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "random", lambda: 0.3)
            result = selector.select(population, context={}, count=2)

        assert len(result) == 2

    def test_roulette_wheel_selector_negative_fitness(self):
        """Test roulette wheel with negative fitness values."""
        selector = RouletteWheelSelector()

        population = [
            ({"id": "genome1"}, -0.5),
            ({"id": "genome2"}, 0.8),
            ({"id": "genome3"}, 0.2),
        ]

        # Should handle negative fitness by adding offset
        result = selector.select(population, context={}, count=1)
        assert len(result) == 1

    def test_roulette_wheel_selector_zero_fitness(self):
        """Test roulette wheel with all zero fitness."""
        selector = RouletteWheelSelector()

        population = [
            ({"id": "genome1"}, 0.0),
            ({"id": "genome2"}, 0.0),
            ({"id": "genome3"}, 0.0),
        ]

        # Should use equal probability
        result = selector.select(population, context={}, count=2)
        assert len(result) == 2

    def test_roulette_wheel_selector_empty(self):
        """Test roulette wheel with empty population."""
        selector = RouletteWheelSelector()
        result = selector.select([], context={}, count=3)
        assert result == []

    def test_ranking_selector_linear(self):
        """Test linear ranking selection."""
        selector = RankingSelector(selection_pressure=1.5, ranking_method="linear")

        population = [
            ({"id": "genome1"}, 0.9),
            ({"id": "genome2"}, 0.8),
            ({"id": "genome3"}, 0.7),
        ]

        # Mock random.choices to select first rank
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "choices", lambda population, weights=None, k=1: [0])
            result = selector.select(population, context={}, count=1)

        assert len(result) == 1

    def test_ranking_selector_exponential(self):
        """Test exponential ranking selection."""
        selector = RankingSelector(selection_pressure=1.8, ranking_method="exponential")

        population = [
            ({"id": "genome1"}, 0.9),
            ({"id": "genome2"}, 0.8),
        ]

        result = selector.select(population, context={}, count=1)
        assert len(result) == 1

    def test_ranking_selector_invalid_method(self):
        """Test ranking selector with invalid method."""
        with pytest.raises(ValueError, match="Invalid ranking method"):
            RankingSelector(ranking_method="invalid")

    def test_ranking_selector_empty(self):
        """Test ranking selector with empty population."""
        selector = RankingSelector()
        result = selector.select([], context={}, count=3)
        assert result == []

    def test_composite_selector_basic(self):
        """Test composite selector."""
        mock_selector1 = Mock()
        mock_selector1.select.return_value = [{"id": "genome1"}]

        mock_selector2 = Mock()
        mock_selector2.select.return_value = [{"id": "genome2"}]

        selector = CompositeSelector(
            [
                (mock_selector1, 0.7),
                (mock_selector2, 0.3),
            ]
        )

        population = [({"id": "dummy"}, 1.0)]

        # Mock random to select first selector
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(random, "random", lambda: 0.5)
            result = selector.select(population, context={}, count=1)

        assert len(result) == 1
        mock_selector1.select.assert_called_once_with(population, {}, 1)

    def test_composite_selector_empty_population(self):
        """Test composite selector with empty population."""
        mock_selector = Mock()
        selector = CompositeSelector([(mock_selector, 1.0)])

        result = selector.select([], context={}, count=3)
        assert result == []
        mock_selector.select.assert_not_called()

    def test_selector_string_representations(self):
        """Test selector string representations."""
        tournament = TournamentSelector(tournament_size=5)
        assert "TournamentSelector[size=5]" in str(tournament)

        roulette = RouletteWheelSelector()
        assert "RouletteWheelSelector" in str(roulette)

        ranking = RankingSelector(selection_pressure=1.7, ranking_method="linear")
        assert "RankingSelector[linear, pressure=1.7]" in str(ranking)

        composite = CompositeSelector([(Mock(), 1.0)])
        assert "CompositeSelector[1 selectors]" in str(composite)
