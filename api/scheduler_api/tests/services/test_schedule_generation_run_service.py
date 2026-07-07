"""Test ScheduleGenerationRunService with simplified approach."""

import pytest
from unittest.mock import MagicMock, create_autospec, patch
from uuid import uuid4
from datetime import datetime, UTC
from sqlmodel import Session

from scheduler_api.services.schedule_generation_run_service import (
    ScheduleGenerationRunService,
)
from scheduler_api.schemas.schedule_generation_run import (
    ScheduleGenerationRunCreate,
    ScheduleGenerationRunUpdate,
    ScheduleGenerationRunResponse,
)
from scheduler_api.db.models.enums import ScheduleGenerationStatus


class TestScheduleGenerationRunService:
    """Test ScheduleGenerationRunService with simplified approach."""

    @pytest.fixture
    def mock_session(self):
        """Mock SQLModel session."""
        return create_autospec(Session)

    @pytest.fixture
    def service(self, mock_session):
        """ScheduleGenerationRunService instance with mocked session."""
        service = ScheduleGenerationRunService(mock_session)
        service.repo = MagicMock()
        return service

    @pytest.fixture
    def sample_run_model(self):
        run = MagicMock()
        run.id = uuid4()
        run.schedule_template_id = uuid4()
        run.schedule_id = None
        run.status = ScheduleGenerationStatus.pending
        run.started_at = None
        run.finished_at = None
        run.parameters = {}
        run.created_at = datetime.now(UTC)
        run.updated_at = datetime.now(UTC)
        return run

    @pytest.fixture
    def sample_run_response(self, sample_run_model):
        return ScheduleGenerationRunResponse(
            id=sample_run_model.id,
            schedule_template_id=sample_run_model.schedule_template_id,
            schedule_id=sample_run_model.schedule_id,
            status=sample_run_model.status,
            started_at=sample_run_model.started_at,
            finished_at=sample_run_model.finished_at,
            parameters=sample_run_model.parameters,
            created_at=sample_run_model.created_at,
            updated_at=sample_run_model.updated_at,
        )

    def test_service_initialization(self, mock_session):
        """Test that service initializes repository with session."""
        service = ScheduleGenerationRunService(mock_session)
        assert service.session == mock_session
        assert hasattr(service, "repo")
        # Repository should be instantiated with the same session
        assert service.repo.session == mock_session

    def test_list_schedule_generation_runs(
        self, service, sample_run_model, sample_run_response
    ):
        # Setup
        service.repo.get_all.return_value = [sample_run_model]

        # Mock mapper function
        with patch(
            "scheduler_api.services.schedule_generation_run_service.to_response"
        ) as mock_to_response:
            mock_responses = [sample_run_response]
            mock_to_response.side_effect = lambda x: (
                mock_responses.pop(0) if mock_responses else MagicMock()
            )

            # Test
            result = service.list_schedule_generation_runs()

        # Verify
        service.repo.get_all.assert_called_once()
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert len(result) == 1

    def test_get_schedule_generation_run_found(
        self, service, sample_run_model, sample_run_response
    ):
        # Setup
        run_id = sample_run_model.id
        service.repo.get_by_id.return_value = sample_run_model

        # Mock mapper function
        with patch(
            "scheduler_api.services.schedule_generation_run_service.to_response"
        ) as mock_to_response:
            mock_to_response.return_value = sample_run_response

            # Test
            result = service.get_schedule_generation_run(run_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(run_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert result == sample_run_response

    def test_get_schedule_generation_run_not_found(self, service):
        # Setup
        run_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.get_schedule_generation_run(run_id)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(run_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read

    def test_create_schedule_generation_run_success(
        self, service, sample_run_model, sample_run_response
    ):
        # Setup
        create_dto = ScheduleGenerationRunCreate(
            schedule_template_id=sample_run_model.schedule_template_id, parameters={}
        )

        # Mock mapper functions
        with patch(
            "scheduler_api.services.schedule_generation_run_service.from_create"
        ) as mock_from_create, patch(
            "scheduler_api.services.schedule_generation_run_service.to_response"
        ) as mock_to_response:
            mock_from_create.return_value = sample_run_model
            mock_to_response.return_value = sample_run_response
            service.repo.add.return_value = sample_run_model

            # Test
            result = service.create_schedule_generation_run(create_dto)

        # Verify
        mock_from_create.assert_called_once_with(create_dto)
        service.repo.add.assert_called_once_with(sample_run_model)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()
        assert result == sample_run_response

    def test_update_schedule_generation_run_success(
        self, service, sample_run_model, sample_run_response
    ):
        # Setup
        run_id = sample_run_model.id
        update_dto = ScheduleGenerationRunUpdate(
            status=ScheduleGenerationStatus.running
        )
        service.repo.get_by_id.return_value = sample_run_model

        # Mock mapper functions
        with patch(
            "scheduler_api.services.schedule_generation_run_service.apply_update"
        ) as mock_apply_update, patch(
            "scheduler_api.services.schedule_generation_run_service.to_response"
        ) as mock_to_response:
            mock_apply_update.return_value = sample_run_model
            mock_to_response.return_value = sample_run_response

            # Test
            result = service.update_schedule_generation_run(run_id, update_dto)

        # Verify
        service.repo.get_by_id.assert_called_once_with(run_id)
        mock_apply_update.assert_called_once_with(sample_run_model, update_dto)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()
        assert result == sample_run_response

    def test_update_schedule_generation_run_not_found(self, service):
        # Setup
        run_id = uuid4()
        update_dto = ScheduleGenerationRunUpdate(
            status=ScheduleGenerationStatus.running
        )
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.update_schedule_generation_run(run_id, update_dto)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(run_id)
        service.session.commit.assert_not_called()  # No commit if not found
        service.session.flush.assert_not_called()  # No flush if not found

    def test_delete_schedule_generation_run_success(self, service, sample_run_model):
        # Setup
        run_id = sample_run_model.id
        service.repo.get_by_id.return_value = sample_run_model
        service.repo.delete = MagicMock()

        # Test
        service.delete_schedule_generation_run(run_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(run_id)
        service.repo.delete.assert_called_once_with(sample_run_model)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_delete_schedule_generation_run_not_found(self, service):
        # Setup
        run_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        with pytest.raises(
            ValueError, match=f"Schedule generation run with id {run_id} not found"
        ):
            service.delete_schedule_generation_run(run_id)

        service.repo.get_by_id.assert_called_once_with(run_id)
        service.session.commit.assert_not_called()  # No commit if error
        service.session.flush.assert_not_called()  # No flush if error
