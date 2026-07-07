"""Test tasks for solve framework."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from scheduler_api.tasks.solve_tasks import schedule_solve_task


class TestSolveTasks:
    """Test solve framework tasks."""

    def test_schedule_solve_task_success(self):
        """Test schedule_solve_task with successful execution."""
        # Setup
        template_id = str(uuid4())
        parameters_dict = {
            "population_size": 100,
            "max_generations": 50,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
        }

        mock_result = Mock()
        mock_result.id = uuid4()
        mock_result.status = "completed"
        mock_result.best_fitness = 0.95
        mock_result.generations = 42
        mock_result.elapsed_time = 1.5
        mock_result.metrics = {"avg_fitness": 0.8}
        mock_result.best_genome = None

        with patch("scheduler_api.tasks.solve_tasks.UUID") as mock_uuid:
            with patch(
                "scheduler_api.tasks.solve_tasks.ScheduleSolveParameters"
            ) as mock_params:
                with patch(
                    "scheduler_api.tasks.solve_tasks.ScheduleSolver"
                ) as mock_solver:
                    with patch(
                        "scheduler_api.tasks.solve_tasks.SolveOrchestrator"
                    ) as mock_orchestrator:
                        # Mock the orchestrator solve method
                        mock_orchestrator_instance = mock_orchestrator.return_value
                        mock_orchestrator_instance.solve.return_value = mock_result

                        # Test
                        result = schedule_solve_task(template_id, parameters_dict)

                        # Verify
                        mock_uuid.assert_called_once_with(template_id)
                        mock_params.assert_called_once_with(**parameters_dict)
                        mock_solver.assert_called_once()
                        mock_orchestrator.assert_called_once()
                        mock_orchestrator_instance.solve.assert_called_once()

                        assert result["status"] == "completed"
                        assert result["best_fitness"] == 0.95
                        assert result["generations"] == 42
                        assert "id" in result

    def test_schedule_solve_task_success_with_genome(self):
        """Test schedule_solve_task with successful execution and genome."""
        # Setup
        template_id = str(uuid4())
        parameters_dict = {
            "population_size": 100,
            "max_generations": 50,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
        }

        mock_result = Mock()
        mock_result.id = uuid4()
        mock_result.status = "completed"
        mock_result.best_fitness = 0.95
        mock_result.generations = 42
        mock_result.elapsed_time = 1.5
        mock_result.metrics = {"avg_fitness": 0.8}
        mock_result.best_genome = Mock()

        with patch("scheduler_api.tasks.solve_tasks.UUID"):
            with patch("scheduler_api.tasks.solve_tasks.ScheduleSolveParameters"):
                with patch("scheduler_api.tasks.solve_tasks.ScheduleSolver"):
                    with patch(
                        "scheduler_api.tasks.solve_tasks.SolveOrchestrator"
                    ) as mock_orchestrator:
                        with patch(
                            "scheduler_api.tasks.solve_tasks.ScheduleGenomeDTO"
                        ) as mock_genome_dto:
                            # Mock the orchestrator solve method
                            mock_orchestrator_instance = mock_orchestrator.return_value
                            mock_orchestrator_instance.solve.return_value = mock_result

                            mock_genome_dto_instance = Mock()
                            mock_genome_dto_instance.model_dump.return_value = {
                                "assignments": []
                            }
                            mock_genome_dto.from_domain.return_value = (
                                mock_genome_dto_instance
                            )

                            # Test
                            result = schedule_solve_task(template_id, parameters_dict)

                            # Verify
                            assert result["status"] == "completed"
                            assert "best_genome" in result
                            assert result["best_genome"] == {"assignments": []}
                            mock_genome_dto.from_domain.assert_called_once_with(
                                mock_result.best_genome
                            )

    def test_schedule_solve_task_invalid_uuid(self):
        """Test schedule_solve_task with invalid UUID."""
        # Setup
        template_id = "invalid-uuid"
        parameters_dict = {"population_size": 100}

        # Test
        result = schedule_solve_task(template_id, parameters_dict)

        # Verify
        assert result["status"] == "failed"
        assert "error_message" in result
        assert "badly formed" in result["error_message"]
        assert result["template_id"] == template_id

    def test_schedule_solve_task_invalid_parameters(self):
        """Test schedule_solve_task with invalid parameters."""
        # Setup
        template_id = str(uuid4())
        parameters_dict = {"invalid_param": "value"}  # Missing required fields

        # Test
        with patch("scheduler_api.tasks.solve_tasks.UUID"):
            with patch(
                "scheduler_api.tasks.solve_tasks.ScheduleSolveParameters"
            ) as mock_params:
                mock_params.side_effect = ValueError("Invalid parameters")

                result = schedule_solve_task(template_id, parameters_dict)

                # Verify
                assert result["status"] == "failed"
                assert "Invalid parameters" in result["error_message"]
                assert result["template_id"] == template_id

    def test_schedule_solve_task_exception_handling(self):
        """Test schedule_solve_task exception handling."""
        # Setup
        template_id = str(uuid4())
        parameters_dict = {"population_size": 100}

        with patch("scheduler_api.tasks.solve_tasks.UUID"):
            with patch("scheduler_api.tasks.solve_tasks.ScheduleSolveParameters"):
                with patch("scheduler_api.tasks.solve_tasks.ScheduleSolver"):
                    with patch(
                        "scheduler_api.tasks.solve_tasks.SolveOrchestrator"
                    ) as mock_orchestrator:
                        mock_orchestrator_instance = mock_orchestrator.return_value
                        mock_orchestrator_instance.solve.side_effect = Exception(
                            "Solve failed"
                        )

                        # Test
                        result = schedule_solve_task(template_id, parameters_dict)

                        # Verify
                        assert result["status"] == "failed"
                        assert "Solve failed" in result["error_message"]
                        assert result["template_id"] == template_id
