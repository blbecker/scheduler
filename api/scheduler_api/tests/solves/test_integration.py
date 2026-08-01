"""Integration tests for enhanced solve engine with real evolution."""

from unittest.mock import Mock, patch
from uuid import uuid4

from scheduler_api.engine.composition import ChainOperator
from scheduler_api.engine.selection import TournamentSelector
from scheduler_api.solves.schedule_solve.callbacks import DatabaseCallback
from scheduler_api.solves.schedule_solve.solver import ScheduleSolver
from scheduler_api.domain.schedule import Schedule
from scheduler_api.solves.schedule_solve.context import ScheduleSolveContext
from scheduler_api.services.schedule_solve_service import ScheduleSolveService


class TestEnhancedEngineIntegration:
    """Integration tests for enhanced evolution engine."""

    def test_database_callback_integration(self):
        """Test that DatabaseCallback integrates with ScheduleSolveService."""
        # Setup
        solve_id = uuid4()
        mock_service = Mock(spec=ScheduleSolveService)

        callback = DatabaseCallback(solve_id, mock_service)

        # Set max generations
        callback.max_generations = 100

        # Create mock population
        mock_population = Mock()
        mock_population.get_best_fitness.return_value = 0.85

        # Test
        callback.on_generation_complete(25, mock_population)

        # Verify
        mock_service.update_schedule_solve_progress.assert_called_once_with(
            solve_id,
            current_generation=25,
            best_fitness=0.85,
            progress=0.25,  # 25/100 = 0.25
        )

    def test_schedule_solver_with_pipeline_types(self):
        """Test that ScheduleSolver works with different pipeline types."""
        # Test default pipeline
        solver_default = ScheduleSolver(pipeline_type="default")
        assert solver_default.pipeline_type == "default"

        # Test advanced pipeline
        solver_advanced = ScheduleSolver(pipeline_type="advanced")
        assert solver_advanced.pipeline_type == "advanced"

        # Test performance pipeline
        solver_performance = ScheduleSolver(pipeline_type="performance")
        assert solver_performance.pipeline_type == "performance"

        # Test that solver creates context (using public method)
        context = solver_default.create_context(
            template_id=uuid4(),
            parameters={"population_size": 100, "max_generations": 50},
        )
        assert isinstance(context, ScheduleSolveContext)

    def test_composition_operators_work_with_real_schedules(self):
        """Test that composition operators work with real Schedule objects."""
        # Create chain operator with mock operators
        mock_operator1 = Mock()
        mock_operator2 = Mock()
        chain_operator = ChainOperator([mock_operator1, mock_operator2])

        # Create a real schedule
        from scheduler_api.domain.schedule import (
            Schedule,
            ShiftAssignment,
            ShiftAssignmentStatus,
        )

        schedule = Schedule()

        # Mock the operators to return modified schedules
        mock_operator1.apply.return_value = schedule
        mock_operator2.apply.return_value = schedule

        # Test chain operator
        mock_context = Mock(spec=ScheduleSolveContext)
        result = chain_operator.apply(schedule, mock_context)

        # Verify
        assert isinstance(result, Schedule)
        mock_operator1.apply.assert_called_once_with(schedule, mock_context)
        mock_operator2.apply.assert_called_once_with(schedule, mock_context)

    def test_enhanced_selection_strategies_integration(self):
        """Test integration of enhanced selection strategies."""
        # Setup tournament selector
        tournament_selector = TournamentSelector(tournament_size=3)

        # Create mock candidates with different fitness values
        population = []
        for i in range(10):
            schedule = Mock(spec=Schedule)
            fitness = 0.1 * i  # 0.0 to 0.9
            population.append((schedule, fitness))

        # Mock context
        context = Mock(spec=ScheduleSolveContext)

        # Test tournament selection
        selected = tournament_selector.select(population, context, 5)

        # Verify
        assert len(selected) == 5
