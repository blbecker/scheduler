"""Test tasks for solve framework."""

import pytest
from unittest.mock import Mock, patch
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

        # Mock the pseudo-task to return success
        with patch(
            "scheduler_api.tasks.solve_tasks.schedule_solve_pseudo_task"
        ) as mock_pseudo:
            mock_pseudo.return_value = {
                "status": "completed",
                "schedule_solve_id": str(uuid4()),
                "best_fitness": 0.95,
                "generations": 42,
                "elapsed_time": 1.5,
                "schedule_id": str(uuid4()),
            }

            # Test
            result = schedule_solve_task(template_id, parameters_dict)

        # Verify
        assert result["status"] == "completed"
        assert "schedule_solve_id" in result
        assert "best_fitness" in result
        assert "generations" in result

    def test_schedule_solve_task_success_with_genome(self):
        """Test schedule_solve_task with successful execution."""
        # Setup
        template_id = str(uuid4())
        parameters_dict = {
            "population_size": 100,
            "max_generations": 50,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
        }

        # Mock the pseudo-task
        with patch(
            "scheduler_api.tasks.solve_tasks.schedule_solve_pseudo_task"
        ) as mock_pseudo:
            mock_pseudo.return_value = {
                "status": "completed",
                "schedule_solve_id": str(uuid4()),
                "best_fitness": 0.95,
                "generations": 42,
            }

            # Test
            result = schedule_solve_task(template_id, parameters_dict)

        # Verify basic structure
        assert "status" in result
        assert "schedule_solve_id" in result
        assert isinstance(result["schedule_solve_id"], str)

    def test_schedule_solve_task_invalid_uuid(self):
        """Test schedule_solve_task with invalid UUID."""
        # Setup
        template_id = "invalid-uuid"
        parameters_dict = {"population_size": 100}

        # Mock the pseudo-task
        with patch(
            "scheduler_api.tasks.solve_tasks.schedule_solve_pseudo_task"
        ) as mock_pseudo:
            mock_pseudo.return_value = {
                "status": "completed",
                "schedule_solve_id": str(uuid4()),
            }

            # Test - legacy task should handle invalid UUID gracefully
            result = schedule_solve_task(template_id, parameters_dict)

        # Verify
        assert "status" in result
        assert "schedule_solve_id" in result

    def test_schedule_solve_task_invalid_parameters(self):
        """Test schedule_solve_task with invalid parameters."""
        # Setup
        template_id = str(uuid4())
        parameters_dict = {"invalid_param": "value"}  # Missing required fields

        # Mock the pseudo-task
        with patch(
            "scheduler_api.tasks.solve_tasks.schedule_solve_pseudo_task"
        ) as mock_pseudo:
            mock_pseudo.return_value = {
                "status": "completed",
                "schedule_solve_id": str(uuid4()),
            }

            # Test - legacy task should handle invalid parameters
            result = schedule_solve_task(template_id, parameters_dict)

        # Verify
        assert "status" in result
        assert "schedule_solve_id" in result

    def test_schedule_solve_task_exception_handling(self):
        """Test schedule_solve_task exception handling."""
        # Setup
        template_id = str(uuid4())
        parameters_dict = {"population_size": 100}

        # Mock the pseudo-task to raise an exception
        with patch(
            "scheduler_api.tasks.solve_tasks.schedule_solve_pseudo_task"
        ) as mock_pseudo:
            mock_pseudo.side_effect = Exception("Solve failed")

            # Test - should re-raise the exception
            with pytest.raises(Exception, match="Solve failed"):
                schedule_solve_task(template_id, parameters_dict)
