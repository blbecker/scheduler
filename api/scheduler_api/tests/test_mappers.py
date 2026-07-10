"""Test mappers for the scheduler API without SQLAlchemy dependency."""

import pytest
from uuid import uuid4
from datetime import datetime, UTC, time
from unittest.mock import MagicMock

# Test the mapper functions directly without SQLAlchemy dependencies
# We'll patch the model imports and test the logic


class TestScheduleSolveMapper:
    """Test ScheduleSolveMapper functions with patched models."""

    def test_to_response_logic(self):
        """Test the logic of to_response function without SQLAlchemy."""
        from scheduler_api.mappers.schedule_solve_mapper import to_response

        # Mock a model
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.schedule_template_id = uuid4()
        mock_model.schedule_id = uuid4()
        mock_model.status = "pending"
        mock_model.started_at = datetime.now(UTC)
        mock_model.finished_at = datetime.now(UTC)
        mock_model.parameters = {"test": "value"}
        mock_model.celery_task_id = "test-task-123"
        mock_model.current_generation = 10
        mock_model.best_fitness = 0.8
        mock_model.progress = 0.5
        mock_model.error_details = "Test error"
        mock_model.created_at = datetime.now(UTC)
        mock_model.updated_at = datetime.now(UTC)

        # Test the function
        response = to_response(mock_model)

        # Verify the response has the right values
        assert response.id == mock_model.id
        assert response.schedule_template_id == mock_model.schedule_template_id
        assert response.schedule_id == mock_model.schedule_id
        assert response.status == mock_model.status
        assert response.started_at == mock_model.started_at
        assert response.finished_at == mock_model.finished_at
        assert response.parameters == mock_model.parameters
        assert response.celery_task_id == mock_model.celery_task_id
        assert response.current_generation == mock_model.current_generation
        assert response.best_fitness == mock_model.best_fitness
        assert response.progress == mock_model.progress
        assert response.error_details == mock_model.error_details
        assert response.created_at == mock_model.created_at
        assert response.updated_at == mock_model.updated_at

    def test_from_create_logic(self):
        """Test the logic of from_create function."""
        from scheduler_api.mappers.schedule_solve_mapper import from_create
        from scheduler_api.db.models.enums import ScheduleSolveStatus

        # Mock imports to avoid SQLAlchemy
        with pytest.MonkeyPatch.context() as mp:
            # Mock ScheduleSolveModel to avoid SQLAlchemy
            mock_model_class = MagicMock()
            mp.setattr(
                "scheduler_api.mappers.schedule_solve_mapper.ScheduleSolveModel",
                mock_model_class,
            )

            # Create test DTO
            template_id = uuid4()
            dto = MagicMock()
            dto.schedule_template_id = template_id
            dto.parameters = {"test": "value"}

            # Test the function
            result = from_create(dto)

            # Verify ScheduleSolveModel was called with correct parameters
            mock_model_class.assert_called_once_with(
                schedule_template_id=template_id,
                parameters={"test": "value"},
                status=ScheduleSolveStatus.pending,
                started_at=None,
                finished_at=None,
                celery_task_id=None,
                current_generation=None,
                best_fitness=None,
                progress=0.0,
                error_details=None,
            )

    def test_apply_update_logic(self):
        """Test the logic of apply_update function."""
        from scheduler_api.mappers.schedule_solve_mapper import apply_update

        # Mock model
        mock_model = MagicMock()
        mock_model.id = uuid4()

        # Mock DTO
        mock_dto = MagicMock()
        mock_dto.model_dump.return_value = {
            "status": "running",
            "celery_task_id": "new-task",
            "progress": 0.5,
        }

        # Test the function
        result = apply_update(mock_model, mock_dto)

        # Verify setattr was called for each field
        assert mock_model.status == "running"
        assert mock_model.celery_task_id == "new-task"
        assert mock_model.progress == 0.5
        assert result is mock_model


class TestScheduleMapper:
    """Test ScheduleMapper functions with patched models."""

    def test_to_response_logic(self):
        """Test the logic of to_response function."""
        from scheduler_api.mappers.schedule_mapper import to_response

        # Mock a model
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.name = "Test Schedule"
        mock_model.schedule_template_id = uuid4()
        mock_model.created_at = datetime.now(UTC)
        mock_model.updated_at = datetime.now(UTC)

        # Test the function
        response = to_response(mock_model)

        # Verify the response has the right values
        assert response.id == mock_model.id
        assert response.name == mock_model.name
        assert response.schedule_template_id == mock_model.schedule_template_id
        assert response.created_at == mock_model.created_at
        assert response.updated_at == mock_model.updated_at

    def test_from_create_logic(self):
        """Test the logic of from_create function."""
        from scheduler_api.mappers.schedule_mapper import from_create

        # Mock imports
        with pytest.MonkeyPatch.context() as mp:
            mock_model_class = MagicMock()
            mp.setattr(
                "scheduler_api.mappers.schedule_mapper.ScheduleModel", mock_model_class
            )

            # Create test DTO
            mock_dto = MagicMock()
            mock_dto.model_dump.return_value = {
                "name": "Test Schedule",
                "schedule_template_id": uuid4(),
            }

            # Test the function
            result = from_create(mock_dto)

            # Verify ScheduleModel was called with correct parameters
            mock_model_class.assert_called_once_with(
                name="Test Schedule",
                schedule_template_id=mock_dto.model_dump.return_value[
                    "schedule_template_id"
                ],
            )

    def test_apply_update_logic(self):
        """Test the logic of apply_update function."""
        from scheduler_api.mappers.schedule_mapper import apply_update

        # Mock model
        mock_model = MagicMock()

        # Mock DTO
        mock_dto = MagicMock()
        mock_dto.model_dump.return_value = {
            "name": "Updated Schedule",
            "schedule_template_id": uuid4(),
        }

        # Test the function
        result = apply_update(mock_model, mock_dto)

        # Verify setattr was called for each field
        assert mock_model.name == "Updated Schedule"
        assert (
            mock_model.schedule_template_id
            == mock_dto.model_dump.return_value["schedule_template_id"]
        )
        assert result is mock_model


class TestScheduleTemplateMapper:
    """Test ScheduleTemplateMapper functions with patched models."""

    def test_to_response_logic(self):
        """Test the logic of to_response function."""
        from scheduler_api.mappers.schedule_template_mapper import to_response

        # Mock a model
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.name = "Test Template"
        mock_model.created_at = datetime.now(UTC)
        mock_model.updated_at = datetime.now(UTC)

        # Test the function
        response = to_response(mock_model)

        # Verify the response has the right values
        assert response.id == mock_model.id
        assert response.name == mock_model.name
        assert response.created_at == mock_model.created_at
        assert response.updated_at == mock_model.updated_at

    def test_from_create_logic(self):
        """Test the logic of from_create function."""
        from scheduler_api.mappers.schedule_template_mapper import from_create

        # Mock imports
        with pytest.MonkeyPatch.context() as mp:
            mock_model_class = MagicMock()
            mp.setattr(
                "scheduler_api.mappers.schedule_template_mapper.ScheduleTemplateModel",
                mock_model_class,
            )

            # Create test DTO
            mock_dto = MagicMock()
            mock_dto.model_dump.return_value = {"name": "Test Template"}

            # Test the function
            result = from_create(mock_dto)

            # Verify ScheduleTemplateModel was called with correct parameters
            mock_model_class.assert_called_once_with(name="Test Template")

    def test_apply_update_logic(self):
        """Test the logic of apply_update function."""
        from scheduler_api.mappers.schedule_template_mapper import apply_update

        # Mock model
        mock_model = MagicMock()

        # Mock DTO
        mock_dto = MagicMock()
        mock_dto.model_dump.return_value = {"name": "Updated Template"}

        # Test the function
        result = apply_update(mock_model, mock_dto)

        # Verify setattr was called
        assert mock_model.name == "Updated Template"
        assert result is mock_model


class TestShiftTemplateMapper:
    """Test ShiftTemplateMapper functions with patched models."""

    def test_to_response_logic(self):
        """Test the logic of to_response function."""
        from scheduler_api.mappers.shift_template_mapper import to_response

        # Mock a model
        schedule_template_id = uuid4()
        start_time = time(9, 0)
        end_time = time(17, 0)
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.schedule_template_id = schedule_template_id
        mock_model.name = "Morning Shift"
        mock_model.start_time = start_time
        mock_model.end_time = end_time
        mock_model.created_at = created_at
        mock_model.updated_at = updated_at

        # Test the function
        response = to_response(mock_model)

        # Verify the response has the right values
        assert response.id == mock_model.id
        assert response.schedule_template_id == schedule_template_id
        assert response.name == "Morning Shift"
        assert response.start_time == start_time
        assert response.end_time == end_time
        assert response.created_at == created_at
        assert response.updated_at == updated_at

    def test_from_create_logic(self):
        """Test the logic of from_create function."""
        from scheduler_api.mappers.shift_template_mapper import from_create

        # Mock imports
        with pytest.MonkeyPatch.context() as mp:
            mock_model_class = MagicMock()
            mp.setattr(
                "scheduler_api.mappers.shift_template_mapper.ShiftTemplateModel",
                mock_model_class,
            )

            # Create test DTO data
            schedule_template_id = uuid4()
            start_time = time(9, 0)
            end_time = time(17, 0)

            mock_dto = MagicMock()
            mock_dto.model_dump.return_value = {
                "schedule_template_id": schedule_template_id,
                "name": "Morning Shift",
                "start_time": start_time,
                "end_time": end_time,
            }

            # Test the function
            result = from_create(mock_dto)

            # Verify ShiftTemplateModel was called with correct parameters
            mock_model_class.assert_called_once_with(
                schedule_template_id=schedule_template_id,
                name="Morning Shift",
                start_time=start_time,
                end_time=end_time,
            )

    def test_apply_update_logic(self):
        """Test the logic of apply_update function."""
        from scheduler_api.mappers.shift_template_mapper import apply_update

        # Mock model
        mock_model = MagicMock()

        # Mock DTO
        mock_dto = MagicMock()
        mock_dto.model_dump.return_value = {
            "name": "Updated Shift",
            "start_time": time(10, 0),
            "end_time": time(18, 0),
        }

        # Test the function
        result = apply_update(mock_model, mock_dto)

        # Verify setattr was called for each field
        assert mock_model.name == "Updated Shift"
        assert mock_model.start_time == time(10, 0)
        assert mock_model.end_time == time(18, 0)
        assert result is mock_model


class TestWorkerMapper:
    """Test WorkerMapper functions with patched models."""

    def test_to_response_logic(self):
        """Test the logic of to_response function."""
        from scheduler_api.mappers.worker_mapper import to_response

        # Mock a model
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.name = "John Doe"
        mock_model.created_at = datetime.now(UTC)
        mock_model.updated_at = datetime.now(UTC)

        # Test the function
        response = to_response(mock_model)

        # Verify the response has the right values
        assert response.id == mock_model.id
        assert response.name == mock_model.name
        assert response.created_at == mock_model.created_at
        assert response.updated_at == mock_model.updated_at

    def test_from_create_logic(self):
        """Test the logic of from_create function."""
        from scheduler_api.mappers.worker_mapper import from_create

        # Mock imports
        with pytest.MonkeyPatch.context() as mp:
            mock_model_class = MagicMock()
            mp.setattr(
                "scheduler_api.mappers.worker_mapper.WorkerModel", mock_model_class
            )

            # Create test DTO
            mock_dto = MagicMock()
            mock_dto.model_dump.return_value = {"name": "John Doe"}

            # Test the function
            result = from_create(mock_dto)

            # Verify WorkerModel was called with correct parameters
            mock_model_class.assert_called_once_with(name="John Doe")

    def test_apply_update_logic(self):
        """Test the logic of apply_update function."""
        from scheduler_api.mappers.worker_mapper import apply_update

        # Mock model
        mock_model = MagicMock()

        # Mock DTO
        mock_dto = MagicMock()
        mock_dto.model_dump.return_value = {"name": "Updated Name"}

        # Test the function
        result = apply_update(mock_model, mock_dto)

        # Verify setattr was called
        assert mock_model.name == "Updated Name"
        assert result is mock_model
