"""Test ScheduleSolveService with simplified approach."""

import pytest
from unittest.mock import MagicMock, create_autospec, patch
from uuid import uuid4
from datetime import datetime, UTC
from sqlmodel import Session

from scheduler_api.services.schedule_solve_service import (
    ScheduleSolveService,
)
from scheduler_api.schemas.schedule_solve import (
    ScheduleSolveCreate,
    ScheduleSolveUpdate,
    ScheduleSolveResponse,
)
from scheduler_api.db.models.enums import ScheduleSolveStatus


class TestScheduleSolveService:
    """Test ScheduleSolveService with simplified approach."""

    @pytest.fixture
    def mock_session(self):
        """Mock SQLModel session."""
        return create_autospec(Session)

    @pytest.fixture
    def service(self, mock_session):
        """ScheduleSolveService instance with mocked session."""
        service = ScheduleSolveService(mock_session)
        service.repo = MagicMock()
        return service

    @pytest.fixture
    def sample_solve_model(self):
        solve = MagicMock()
        solve.id = uuid4()
        solve.schedule_template_id = uuid4()
        solve.schedule_id = None
        solve.status = ScheduleSolveStatus.pending
        solve.started_at = None
        solve.finished_at = None
        solve.celery_task_id = None
        solve.current_generation = None
        solve.best_fitness = None
        solve.progress = 0.0
        solve.error_details = None
        solve.parameters = {}
        solve.created_at = datetime.now(UTC)
        solve.updated_at = datetime.now(UTC)
        return solve

    @pytest.fixture
    def sample_solve_response(self, sample_solve_model):
        return ScheduleSolveResponse(
            id=sample_solve_model.id,
            schedule_template_id=sample_solve_model.schedule_template_id,
            schedule_id=sample_solve_model.schedule_id,
            status=sample_solve_model.status,
            started_at=sample_solve_model.started_at,
            finished_at=sample_solve_model.finished_at,
            parameters=sample_solve_model.parameters,
            celery_task_id=sample_solve_model.celery_task_id,
            current_generation=sample_solve_model.current_generation,
            best_fitness=sample_solve_model.best_fitness,
            progress=sample_solve_model.progress,
            error_details=sample_solve_model.error_details,
            created_at=sample_solve_model.created_at,
            updated_at=sample_solve_model.updated_at,
        )

    def test_service_initialization(self, mock_session):
        """Test that service initializes repository with session."""
        service = ScheduleSolveService(mock_session)
        assert service.session == mock_session
        assert hasattr(service, "repo")
        # Repository should be instantiated with the same session
        assert service.repo.session == mock_session

    def test_list_schedule_solves(
        self, service, sample_solve_model, sample_solve_response
    ):
        # Setup
        service.repo.get_all.return_value = [sample_solve_model]

        # Mock mapper function
        with patch(
            "scheduler_api.services.schedule_solve_service.to_response"
        ) as mock_to_response:
            mock_responses = [sample_solve_response]
            mock_to_response.side_effect = lambda x: (
                mock_responses.pop(0) if mock_responses else MagicMock()
            )

            # Test
            result = service.list_schedule_solves()

        # Verify
        service.repo.get_all.assert_called_once()
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert len(result) == 1

    def test_get_schedule_solve_found(
        self, service, sample_solve_model, sample_solve_response
    ):
        # Setup
        solve_id = sample_solve_model.id
        service.repo.get_by_id.return_value = sample_solve_model

        # Mock mapper function
        with patch(
            "scheduler_api.services.schedule_solve_service.to_response"
        ) as mock_to_response:
            mock_to_response.return_value = sample_solve_response

            # Test
            result = service.get_schedule_solve(solve_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert result == sample_solve_response

    def test_get_schedule_solve_not_found(self, service):
        # Setup
        solve_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.get_schedule_solve(solve_id)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read

    def test_create_schedule_solve_success(
        self, service, sample_solve_model, sample_solve_response
    ):
        # Setup
        create_dto = ScheduleSolveCreate(
            schedule_template_id=sample_solve_model.schedule_template_id, parameters={}
        )

        # Mock mapper functions
        with patch(
            "scheduler_api.services.schedule_solve_service.from_create"
        ) as mock_from_create, patch(
            "scheduler_api.services.schedule_solve_service.to_response"
        ) as mock_to_response:
            mock_from_create.return_value = sample_solve_model
            mock_to_response.return_value = sample_solve_response
            service.repo.add.return_value = sample_solve_model

            # Test
            result = service.create_schedule_solve(create_dto)

        # Verify
        mock_from_create.assert_called_once_with(create_dto)
        service.repo.add.assert_called_once_with(sample_solve_model)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()
        assert result == sample_solve_response

    def test_update_schedule_solve_success(
        self, service, sample_solve_model, sample_solve_response
    ):
        # Setup
        solve_id = sample_solve_model.id
        update_dto = ScheduleSolveUpdate(status=ScheduleSolveStatus.running)
        service.repo.get_by_id.return_value = sample_solve_model

        # Mock mapper functions
        with patch(
            "scheduler_api.services.schedule_solve_service.apply_update"
        ) as mock_apply_update, patch(
            "scheduler_api.services.schedule_solve_service.to_response"
        ) as mock_to_response:
            mock_apply_update.return_value = sample_solve_model
            mock_to_response.return_value = sample_solve_response

            # Test
            result = service.update_schedule_solve(solve_id, update_dto)

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        mock_apply_update.assert_called_once_with(sample_solve_model, update_dto)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()
        assert result == sample_solve_response

    def test_update_schedule_solve_not_found(self, service):
        # Setup
        solve_id = uuid4()
        update_dto = ScheduleSolveUpdate(status=ScheduleSolveStatus.running)
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.update_schedule_solve(solve_id, update_dto)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.session.commit.assert_not_called()  # No commit if not found
        service.session.flush.assert_not_called()  # No flush if not found

    def test_delete_schedule_solve_success(self, service, sample_solve_model):
        # Setup
        solve_id = sample_solve_model.id
        service.repo.get_by_id.return_value = sample_solve_model
        service.repo.delete = MagicMock()

        # Test
        service.delete_schedule_solve(solve_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.repo.delete.assert_called_once_with(sample_solve_model)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_delete_schedule_solve_not_found(self, service):
        # Setup
        solve_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        with pytest.raises(
            ValueError, match=f"Schedule solve with id {solve_id} not found"
        ):
            service.delete_schedule_solve(solve_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.repo.delete.assert_not_called()  # repo.delete won't be mocked
        service.session.flush.assert_not_called()
        service.session.commit.assert_not_called()

    def test_update_schedule_solve_status_success(self, service, sample_solve_model):
        """Test updating schedule solve status with timestamps."""
        solve_id = sample_solve_model.id

        # Mock repository
        service.repo.get_by_id.return_value = sample_solve_model

        # Mock timestamp updates
        from datetime import datetime, UTC

        sample_solve_model.started_at = None
        sample_solve_model.finished_at = None

        # Test updating to running status
        service.update_schedule_solve_status(solve_id, ScheduleSolveStatus.running)

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        assert sample_solve_model.status == ScheduleSolveStatus.running
        assert sample_solve_model.started_at is not None
        assert sample_solve_model.finished_at is None
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_update_schedule_solve_status_with_completion(
        self, service, sample_solve_model
    ):
        """Test updating schedule solve status to completed."""
        solve_id = sample_solve_model.id

        # Mock repository
        service.repo.get_by_id.return_value = sample_solve_model

        # Mock timestamp updates
        from datetime import datetime, UTC

        sample_solve_model.started_at = datetime.now(UTC)
        sample_solve_model.finished_at = None

        # Test updating to completed status
        service.update_schedule_solve_status(solve_id, ScheduleSolveStatus.completed)

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        assert sample_solve_model.status == ScheduleSolveStatus.completed
        assert sample_solve_model.finished_at is not None
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_update_schedule_solve_status_with_kwargs(
        self, service, sample_solve_model
    ):
        """Test updating schedule solve status with additional fields."""
        solve_id = sample_solve_model.id

        # Mock repository
        service.repo.get_by_id.return_value = sample_solve_model

        # Test updating with additional kwargs
        service.update_schedule_solve_status(
            solve_id,
            ScheduleSolveStatus.running,
            celery_task_id="test-task-123",
            progress=0.5,
            current_generation=10,
            best_fitness=0.8,
        )

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        assert sample_solve_model.status == ScheduleSolveStatus.running
        assert sample_solve_model.celery_task_id == "test-task-123"
        assert sample_solve_model.progress == 0.5
        assert sample_solve_model.current_generation == 10
        assert sample_solve_model.best_fitness == 0.8
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_update_schedule_solve_status_not_found(self, service):
        """Test updating schedule solve status when solve not found."""
        solve_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        with pytest.raises(
            ValueError, match=f"Schedule solve with id {solve_id} not found"
        ):
            service.update_schedule_solve_status(solve_id, ScheduleSolveStatus.running)

        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.session.flush.assert_not_called()
        service.session.commit.assert_not_called()

    def test_update_schedule_solve_progress_success(self, service, sample_solve_model):
        """Test updating schedule solve progress metrics."""
        solve_id = sample_solve_model.id

        # Mock repository
        service.repo.get_by_id.return_value = sample_solve_model

        # Initial values
        sample_solve_model.current_generation = 5
        sample_solve_model.best_fitness = 0.6
        sample_solve_model.progress = 0.1

        # Test updating progress
        service.update_schedule_solve_progress(
            solve_id, current_generation=25, best_fitness=0.9, progress=0.5
        )

        # Verify
        service.repo.get_by_id.assert_called_once_with(solve_id)
        assert sample_solve_model.current_generation == 25
        assert sample_solve_model.best_fitness == 0.9
        assert sample_solve_model.progress == 0.5
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_update_schedule_solve_progress_not_found(self, service):
        """Test updating schedule solve progress when solve not found."""
        solve_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        with pytest.raises(
            ValueError, match=f"Schedule solve with id {solve_id} not found"
        ):
            service.update_schedule_solve_progress(solve_id, current_generation=10)

        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.session.flush.assert_not_called()
        service.session.commit.assert_not_called()

    def test_complete_schedule_solve_success(self, service, sample_solve_model):
        """Test marking schedule solve as completed."""
        solve_id = sample_solve_model.id
        schedule_id = uuid4()

        # Mock repository
        service.repo.get_by_id.return_value = sample_solve_model

        # Mock update_schedule_solve_status method
        with patch.object(
            service, "update_schedule_solve_status"
        ) as mock_update_status:
            # Test
            service.complete_schedule_solve(solve_id, schedule_id)

            # Verify
            mock_update_status.assert_called_once_with(
                solve_id,
                ScheduleSolveStatus.completed,
                schedule_id=schedule_id,
                progress=1.0,
            )

    def test_fail_schedule_solve_success(self, service, sample_solve_model):
        """Test marking schedule solve as failed."""
        solve_id = sample_solve_model.id
        error_details = "Test error message"

        # Mock repository
        service.repo.get_by_id.return_value = sample_solve_model

        # Mock update_schedule_solve_status method
        with patch.object(
            service, "update_schedule_solve_status"
        ) as mock_update_status:
            # Test
            service.fail_schedule_solve(solve_id, error_details)

            # Verify
            mock_update_status.assert_called_once_with(
                solve_id, ScheduleSolveStatus.failed, error_details=error_details
            )

    def test_create_schedule_from_solve_success(self, service, sample_solve_model):
        """Test creating schedule from solve."""
        solve_id = sample_solve_model.id
        schedule_name = "Test Schedule"

        # Mock repository
        service.repo.get_by_id.return_value = sample_solve_model

        # Mock the ScheduleModel import to avoid SQLAlchemy issues
        with patch(
            "scheduler_api.db.models.schedules.schedule.ScheduleModel"
        ) as mock_schedule_model:
            mock_schedule = MagicMock()
            mock_schedule.name = schedule_name
            mock_schedule.schedule_template_id = sample_solve_model.schedule_template_id
            mock_schedule.schedule_solve_id = sample_solve_model.id
            mock_schedule_model.return_value = mock_schedule

            # Test
            result = service.create_schedule_from_solve(solve_id, schedule_name)

            # Verify
            service.repo.get_by_id.assert_called_once_with(solve_id)
            mock_schedule_model.assert_called_once_with(
                name=schedule_name,
                schedule_template_id=sample_solve_model.schedule_template_id,
                schedule_solve_id=sample_solve_model.id,
            )
            service.session.add.assert_called_once_with(mock_schedule)
            service.session.flush.assert_called_once()
            service.session.commit.assert_called_once()
            assert result == mock_schedule

    def test_create_schedule_from_solve_not_found(self, service):
        """Test creating schedule from solve when solve not found."""
        solve_id = uuid4()
        schedule_name = "Test Schedule"
        service.repo.get_by_id.return_value = None

        # Test & Verify
        with pytest.raises(
            ValueError, match=f"Schedule solve with id {solve_id} not found"
        ):
            service.create_schedule_from_solve(solve_id, schedule_name)

        service.repo.get_by_id.assert_called_once_with(solve_id)
        service.session.add.assert_not_called()
        service.session.flush.assert_not_called()
        service.session.commit.assert_not_called()
