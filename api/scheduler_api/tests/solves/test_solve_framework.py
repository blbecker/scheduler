"""Tests for solves framework."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime, UTC

from scheduler_api.solves.schedule_solve.solver import ScheduleSolver
from scheduler_api.engine.orchestrator import SolveOrchestrator
from scheduler_api.solves.schedule_solve.genome import ScheduleGenomeDTO
from scheduler_api.schemas.solve import ScheduleSolveParameters


class TestScheduleSolver:
    """Test the ScheduleSolver class."""

    def test_solver_class_constants(self):
        """Test that solver has correct default parameters."""
        assert hasattr(ScheduleSolver, "DEFAULT_PARAMETERS")
        assert ScheduleSolver.DEFAULT_PARAMETERS["population_size"] == 10
        assert ScheduleSolver.DEFAULT_PARAMETERS["max_generations"] == 20
        assert ScheduleSolver.DEFAULT_PARAMETERS["mutation_rate"] == 0.1
        assert ScheduleSolver.DEFAULT_PARAMETERS["selection_top_n"] == 5
        assert ScheduleSolver.DEFAULT_PARAMETERS["elite_size"] == 1

    def test_solver_create_context(self):
        """Test that solver can create context."""
        solver = ScheduleSolver()
        template_id = uuid4()

        context = solver.create_context(template_id, {})

        assert context is not None
        assert context.template_id == template_id
        assert len(context.worker_ids) == 3  # Mock has 3 workers
        assert len(context.shift_ids) == 5  # Mock has 5 shifts

    def test_solver_create_pipeline(self):
        """Test that solver can create pipeline."""
        solver = ScheduleSolver()
        pipeline = solver.create_pipeline()

        assert pipeline is not None
        assert len(pipeline.seeders) == 1
        assert len(pipeline.genome_operators) == 1
        assert len(pipeline.scorers) == 1
        assert len(pipeline.constraints) == 1
        assert pipeline.selector is not None
        assert len(pipeline.stop_conditions) == 1

    def test_solver_create_initial_population(self):
        """Test that solver can create initial population."""
        solver = ScheduleSolver()

        # Mock the context and seeder
        mock_context = Mock()
        mock_seeder = Mock()
        mock_seeder.seed.return_value = [Mock(), Mock()]

        with patch.object(solver, "create_pipeline") as mock_pipeline:
            mock_pipeline_instance = Mock()
            mock_pipeline_instance.seeders = [mock_seeder]
            mock_pipeline.return_value = mock_pipeline_instance

            population = solver.create_initial_population(mock_context, 2)

            assert len(population) == 2
            mock_seeder.seed.assert_called_once_with(mock_context, 2)


class TestSolveOrchestrator:
    """Test the SolveOrchestrator class."""

    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly."""
        orchestrator = SolveOrchestrator()

        assert orchestrator is not None
        assert orchestrator.evolution_engine is not None

    def test_solve_result_dataclass(self):
        """Test the SolveResult dataclass."""
        from scheduler_api.engine.orchestrator import SolveResult

        result = SolveResult(
            status="completed",
            best_fitness=0.85,
            generations=10,
            elapsed_time=2.5,
            metrics={"avg_fitness": 0.7},
        )

        assert result.status == "completed"
        assert result.best_fitness == 0.85
        assert result.generations == 10
        assert result.elapsed_time == 2.5
        assert result.metrics["avg_fitness"] == 0.7

        # Test to_dict method
        result_dict = result.to_dict()
        assert "id" in result_dict
        assert result_dict["status"] == "completed"
        assert result_dict["best_fitness"] == 0.85

    @patch("scheduler_api.engine.orchestrator.EvolutionEngine")
    def test_solve_with_mock_solvable(self, mock_evolution_engine):
        """Test solve execution with mocked solvable."""
        template_id = uuid4()

        # Create mock solvable
        mock_solvable = Mock(spec=ScheduleSolver)

        # Mock context
        mock_context = Mock()
        mock_context.template_id = template_id
        mock_solvable.create_context.return_value = mock_context

        # Mock create_initial_population to return list
        mock_population = Mock()
        mock_population.get_top_n.return_value = []
        mock_population.get_best_fitness.return_value = 0.8
        mock_population.size.return_value = 10
        mock_population.get_average_fitness.return_value = 0.6
        mock_population.get_worst_fitness.return_value = 0.4
        mock_population.get_fitness_range.return_value = (0.4, 0.8)
        mock_population.get_best.return_value = Mock(fitness=0.8, genome=Mock())
        mock_solvable.create_initial_population.return_value = mock_population

        # Mock pipeline
        mock_pipeline = Mock()
        mock_pipeline.seeders = [Mock()]
        mock_pipeline.seeders[0].seed.return_value = [Mock(), Mock()]
        mock_pipeline.scorers = [Mock()]
        mock_pipeline.scorers[0].score.side_effect = lambda genome: 0.5
        mock_pipeline.constraints = [Mock()]
        mock_pipeline.constraints[0].check.return_value = True
        mock_pipeline.selector = Mock()
        mock_pipeline.selector.select.side_effect = lambda population, n: population[:n]
        mock_pipeline.stop_conditions = [Mock()]
        mock_pipeline.stop_conditions[0].should_stop.side_effect = [False, False, True]

        mock_solvable.create_pipeline.return_value = mock_pipeline

        # Mock evolution engine
        mock_engine_instance = Mock()
        # Mock evolve_population to return a Population mock
        mock_evolved_population = Mock()
        mock_evolved_population.get_best_fitness.return_value = 0.8
        mock_evolved_population.get_best.return_value = Mock(fitness=0.8, genome=Mock())
        mock_evolved_population.size.return_value = 10
        mock_evolved_population.get_average_fitness.return_value = 0.6
        mock_evolved_population.get_worst_fitness.return_value = 0.4
        mock_evolved_population.get_fitness_range.return_value = (0.4, 0.8)
        mock_evolved_population.get_top_n.return_value = []
        mock_engine_instance.evolve_population.return_value = mock_evolved_population
        mock_evolution_engine.return_value = mock_engine_instance

        # Also mock the log_progress method to avoid formatting issues
        with patch.object(SolveOrchestrator, "_log_progress"):
            orchestrator = SolveOrchestrator(mock_engine_instance)

            parameters = {
                "population_size": 10,
                "max_generations": 20,
            }

            # Run solve
            result = orchestrator.solve(mock_solvable, template_id, parameters)

            assert result is not None
            assert result.best_fitness == 0.8
            assert result.generations == 3
            assert result.status == "completed"


class TestSolveSchemas:
    """Test the solve schemas."""

    def test_schedule_solve_parameters(self):
        """Test parameter validation."""
        # Valid parameters
        params = ScheduleSolveParameters(
            population_size=50,
            max_generations=100,
            mutation_rate=0.1,
            selection_top_n=25,
            elite_size=1,
        )

        assert params.population_size == 50
        assert params.max_generations == 100

        # Invalid parameters should raise validation error
        with pytest.raises(ValueError):
            ScheduleSolveParameters(population_size=0)

        with pytest.raises(ValueError):
            ScheduleSolveParameters(mutation_rate=1.5)

    def test_parameters_defaults(self):
        """Test that defaults are applied correctly."""
        params = ScheduleSolveParameters()

        assert params.population_size == 50
        assert params.max_generations == 100
        assert params.mutation_rate == 0.1
        assert params.selection_top_n == 25
        assert params.elite_size == 1


class TestScheduleGenomeDTO:
    """Test the ScheduleGenome DTO serialization."""

    def test_dto_serialization(self):
        """Test that genome can be serialized and deserialized."""
        # Create a mock genome
        genome = Mock()
        genome.assignments = {uuid4(): [uuid4(), uuid4()]}

        # Convert to DTO
        dto = ScheduleGenomeDTO.from_domain(genome)

        assert dto.assignments is not None
        assert len(dto.assignments) == 1

        # Convert back to dict
        dto_dict = dto.model_dump()

        assert "assignments" in dto_dict

    def test_dto_to_domain(self):
        """Test that DTO can be converted to domain object."""
        shift_id = uuid4()
        worker_id1 = uuid4()
        worker_id2 = uuid4()

        assignments = {str(shift_id): [str(worker_id1), str(worker_id2)]}

        dto = ScheduleGenomeDTO(assignments=assignments)

        domain = dto.to_domain()

        assert shift_id in domain.assignments
        assert worker_id1 in domain.assignments[shift_id]
        assert worker_id2 in domain.assignments[shift_id]

    def test_dto_round_trip(self):
        """Test full round-trip conversion."""
        # Create domain genome
        shift_id = uuid4()
        worker_id1 = uuid4()
        worker_id2 = uuid4()

        from scheduler_api.solves.schedule_solve.genome import ScheduleGenome

        domain_genome = ScheduleGenome(assignments={shift_id: [worker_id1, worker_id2]})

        # Convert to DTO
        dto = ScheduleGenomeDTO.from_domain(domain_genome)

        # Convert back to domain
        restored_genome = dto.to_domain()

        assert restored_genome.assignments == domain_genome.assignments
