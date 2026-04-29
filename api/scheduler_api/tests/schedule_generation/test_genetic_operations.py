"""Test genetic operations (stub implementations)."""

import pytest
from unittest.mock import patch
from uuid import uuid4
from scheduler_api.genetic.ga_operations import (
    generate_initial_population,
    score_population,
    mutate_population,
    breed_population,
    cull_population,
    select_best_schedule,
)


class TestGeneticOperations:
    """Test genetic algorithm operations."""

    def test_generate_initial_population(
        self, sample_schedule_layout, mock_random_uniform
    ):
        """Test initial population generation."""
        population = generate_initial_population(sample_schedule_layout, size=10)

        assert population.generation == 0
        assert population.layout_id == sample_schedule_layout.id
        assert population.size() == 10

        # Check schedules have names and fitness values
        for i, schedule in enumerate(population.schedules):
            assert schedule.name == f"Schedule_{i}"
            assert schedule.fitness == 0.5  # Mocked random.uniform returns 0.5

    def test_score_population(self, sample_population, mock_random_uniform):
        """Test population scoring."""
        # Clear fitness values to test scoring
        for schedule in sample_population.schedules:
            schedule.fitness = None

        scored_population = score_population(sample_population)

        # All schedules should now have fitness values
        for schedule in scored_population.schedules:
            assert schedule.fitness is not None
            assert schedule.fitness == 0.5  # Mocked random.uniform returns 0.5

        # Original population should be modified (in-place)
        assert sample_population is scored_population

    def test_score_population_already_scored(self, sample_population):
        """Test scoring population that already has fitness values."""
        # Set specific fitness values
        for schedule in sample_population.schedules:
            schedule.fitness = 0.8

        scored_population = score_population(sample_population)

        # Fitness values should remain unchanged
        for schedule in scored_population.schedules:
            assert schedule.fitness == 0.8

    def test_mutate_population(self, sample_population, mock_random_random):
        """Test population mutation."""
        # Set initial fitness values
        for schedule in sample_population.schedules:
            schedule.fitness = 0.5

        with patch("random.uniform", return_value=0.1):
            mutated_population = mutate_population(sample_population, mutation_rate=1.0)

        # With mutation_rate=1.0 and mock_random_random=0.5 (<1.0), all should mutate
        # Mocked random.uniform returns 0.1, so fitness becomes 0.5 + 0.1 = 0.6
        for schedule in mutated_population.schedules:
            assert schedule.fitness == 0.6

        # Original population should be modified (in-place)
        assert sample_population is mutated_population

    def test_mutate_population_no_mutation(self, sample_population, mock_random_random):
        """Test population mutation with no mutations applied."""
        # Set initial fitness values
        for schedule in sample_population.schedules:
            schedule.fitness = 0.5

        # Mock random.random to return 1.0 (greater than mutation_rate)
        with patch("random.random", return_value=1.0):
            mutated_population = mutate_population(sample_population, mutation_rate=0.5)

        # No mutations should occur
        for schedule in mutated_population.schedules:
            assert schedule.fitness == 0.5

    def test_mutate_population_clamping(self, sample_population, mock_random_random):
        """Test mutation fitness clamping to [0.0, 1.0] range."""
        # Set initial fitness values
        for schedule in sample_population.schedules:
            schedule.fitness = 0.95

        # Mock random.uniform to return 0.1 (would push fitness to 1.05, should clamp to 1.0)
        with patch("random.uniform", return_value=0.1):
            mutated_population = mutate_population(sample_population, mutation_rate=1.0)

        # Fitness should be clamped to 1.0
        for schedule in mutated_population.schedules:
            assert schedule.fitness == 1.0

    def test_breed_population(self, sample_population, mock_random_random):
        """Test population breeding/crossover."""
        # Create a population with multiple schedules
        from scheduler_api.domain.population import Population
        from scheduler_api.domain.schedule import Schedule

        schedules = [
            Schedule(name="Parent1", fitness=0.9),
            Schedule(name="Parent2", fitness=0.8),
            Schedule(name="Parent3", fitness=0.7),
            Schedule(name="Parent4", fitness=0.6),
        ]

        population = Population(
            generation=1,
            schedules=schedules,
            layout_id=sample_population.layout_id,
        )

        with patch("random.random", return_value=0.5):  # < crossover_rate
            bred_population = breed_population(population, crossover_rate=0.8)

        # Should create offspring (2 pairs * 1 child each = 2 children)
        assert bred_population.size() == 6  # 4 parents + 2 children

        # Check child names
        child_names = [
            s.name for s in bred_population.schedules if s.name.startswith("Child")
        ]
        assert len(child_names) == 2
        assert "Child_0" in child_names
        assert "Child_1" in child_names

        # Check child fitness (average of parents)
        child_fitness = [
            s.fitness for s in bred_population.schedules if s.name.startswith("Child")
        ]
        assert child_fitness[0] == (0.9 + 0.8) / 2  # Child of Parent1 and Parent2
        assert child_fitness[1] == (0.7 + 0.6) / 2  # Child of Parent3 and Parent4

    def test_breed_population_no_crossover(self, sample_population, mock_random_random):
        """Test breeding with no crossover."""
        # Create a population with multiple schedules
        from scheduler_api.domain.population import Population
        from scheduler_api.domain.schedule import Schedule

        schedules = [
            Schedule(name="Parent1", fitness=0.9),
            Schedule(name="Parent2", fitness=0.8),
        ]

        population = Population(
            generation=1,
            schedules=schedules,
            layout_id=sample_population.layout_id,
        )

        # Mock random.random to return 1.0 (greater than crossover_rate)
        with patch("random.random", return_value=1.0):
            bred_population = breed_population(population, crossover_rate=0.5)

        # No offspring should be created
        assert bred_population.size() == 2

    def test_breed_population_insufficient_parents(self):
        """Test breeding with insufficient parents."""
        from scheduler_api.domain.population import Population
        from scheduler_api.domain.schedule import Schedule

        # Single schedule
        population = Population(
            generation=1,
            schedules=[Schedule(name="Only", fitness=0.9)],
            layout_id=uuid4(),
        )

        bred_population = breed_population(population, crossover_rate=1.0)

        # No breeding should occur with only one schedule
        assert bred_population.size() == 1

    def test_cull_population(self):
        """Test population culling."""
        from scheduler_api.domain.population import Population
        from scheduler_api.domain.schedule import Schedule

        # Create population with varying fitness
        schedules = [
            Schedule(name="Best", fitness=0.9),
            Schedule(name="Good", fitness=0.7),
            Schedule(name="Average", fitness=0.5),
            Schedule(name="Poor", fitness=0.3),
            Schedule(name="Worst", fitness=0.1),
        ]

        population = Population(
            generation=1,
            schedules=schedules,
            layout_id=uuid4(),
        )

        # Cull to top 3
        culled_population = cull_population(population, target_size=3)

        assert culled_population.size() == 3

        # Should keep schedules with highest fitness
        remaining_names = [s.name for s in culled_population.schedules]
        assert "Best" in remaining_names
        assert "Good" in remaining_names
        assert "Average" in remaining_names
        assert "Poor" not in remaining_names
        assert "Worst" not in remaining_names

    def test_cull_population_no_culling_needed(self, sample_population):
        """Test culling when population is already at or below target size."""
        original_size = sample_population.size()

        # Try to cull to a larger size
        culled_population = cull_population(
            sample_population, target_size=original_size + 5
        )

        # Population should remain unchanged
        assert culled_population.size() == original_size
        assert sample_population is culled_population

    def test_select_best_schedule(self):
        """Test selecting the best schedule from population."""
        from scheduler_api.domain.population import Population
        from scheduler_api.domain.schedule import Schedule

        # Create population with varying fitness
        schedules = [
            Schedule(name="Average", fitness=0.5),
            Schedule(name="Best", fitness=0.9),
            Schedule(name="Good", fitness=0.7),
        ]

        population = Population(
            generation=1,
            schedules=schedules,
            layout_id=uuid4(),
        )

        best_schedule = select_best_schedule(population)

        assert best_schedule.name == "Best"
        assert best_schedule.fitness == 0.9

    def test_select_best_schedule_empty_population(self):
        """Test selecting best schedule from empty population raises error."""
        from scheduler_api.domain.population import Population

        empty_population = Population()

        with pytest.raises(ValueError, match="Population has no schedules"):
            select_best_schedule(empty_population)

    def test_genetic_pipeline_integration(
        self, sample_schedule_layout, mock_random_uniform, mock_random_random
    ):
        """Test integration of all genetic operations in a pipeline."""
        # 1. Generate initial population
        population = generate_initial_population(sample_schedule_layout, size=20)
        assert population.size() == 20
        assert population.generation == 0

        # 2. Score population
        scored_population = score_population(population)
        assert scored_population is population

        # 3. Mutate population
        with patch("random.uniform", return_value=0.05):
            mutated_population = mutate_population(scored_population, mutation_rate=0.1)
        assert mutated_population is population

        # 4. Breed population
        with patch("random.random", return_value=0.5):  # < crossover_rate
            bred_population = breed_population(mutated_population, crossover_rate=0.8)
        assert bred_population is population
        assert bred_population.size() > 20  # Should have offspring

        # 5. Cull population
        culled_population = cull_population(bred_population, target_size=20)
        assert culled_population is population
        assert culled_population.size() == 20

        # 6. Select best schedule
        best_schedule = select_best_schedule(culled_population)
        assert best_schedule is not None
        assert best_schedule.fitness is not None
