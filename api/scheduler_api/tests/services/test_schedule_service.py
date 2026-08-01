"""Test ScheduleService with simplified approach."""

import pytest
from unittest.mock import MagicMock, create_autospec, patch
from uuid import uuid4
from datetime import datetime, UTC
from sqlmodel import Session

from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.schemas.schedule_crud import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
)


class TestScheduleService:
    """Test ScheduleService with simplified approach."""

    @pytest.fixture
    def mock_session(self):
        """Mock SQLModel session."""
        return create_autospec(Session)

    @pytest.fixture
    def service(self, mock_session):
        """ScheduleService instance with mocked session."""
        service = ScheduleService(mock_session)
        service.repo = MagicMock()
        return service

    @pytest.fixture
    def sample_schedule_model(self):
        schedule = MagicMock()
        schedule.id = uuid4()
        schedule.name = "January 2024 Schedule"
        schedule.schedule_template_id = uuid4()
        schedule.created_at = datetime.now(UTC)
        schedule.updated_at = datetime.now(UTC)
        return schedule

    @pytest.fixture
    def sample_schedule_response(self, sample_schedule_model):
        return ScheduleResponse(
            id=sample_schedule_model.id,
            name=sample_schedule_model.name,
            schedule_template_id=sample_schedule_model.schedule_template_id,
            created_at=sample_schedule_model.created_at,
            updated_at=sample_schedule_model.updated_at,
        )

    def test_service_initialization(self, mock_session):
        """Test that service initializes repository with session."""
        service = ScheduleService(mock_session)
        assert service.session == mock_session
        assert hasattr(service, "repo")
        # Repository should be instantiated with the same session
        assert service.repo.session == mock_session

    def test_list_schedules(
        self, service, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        service.repo.get_all.return_value = [sample_schedule_model]

        # Mock mapper function
        with patch(
            "scheduler_api.services.schedule_service.to_response"
        ) as mock_to_response:
            mock_responses = [sample_schedule_response]
            mock_to_response.side_effect = lambda x: (
                mock_responses.pop(0) if mock_responses else MagicMock()
            )

            # Test
            result = service.list_schedules()

        # Verify
        service.repo.get_all.assert_called_once()
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert len(result) == 1

    def test_get_schedule_found(
        self, service, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        schedule_id = sample_schedule_model.id
        service.repo.get_by_id.return_value = sample_schedule_model

        # Mock mapper function
        with patch(
            "scheduler_api.services.schedule_service.to_response"
        ) as mock_to_response:
            mock_to_response.return_value = sample_schedule_response

            # Test
            result = service.get_schedule(schedule_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(schedule_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert result == sample_schedule_response

    def test_get_schedule_not_found(self, service):
        # Setup
        schedule_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.get_schedule(schedule_id)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(schedule_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read

    def test_create_schedule_success(
        self, service, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        create_dto = ScheduleCreate(
            name="January 2024 Schedule",
            schedule_template_id=sample_schedule_model.schedule_template_id,
        )

        # Mock mapper functions
        with patch(
            "scheduler_api.services.schedule_service.from_create"
        ) as mock_from_create, patch(
            "scheduler_api.services.schedule_service.to_response"
        ) as mock_to_response:
            mock_from_create.return_value = sample_schedule_model
            mock_to_response.return_value = sample_schedule_response
            service.repo.add.return_value = sample_schedule_model

            # Test
            result = service.create_schedule(create_dto)

        # Verify
        mock_from_create.assert_called_once_with(create_dto)
        service.repo.add.assert_called_once_with(sample_schedule_model)
        assert service.session.flush.call_count >= 1
        service.session.commit.assert_called_once()
        assert result == sample_schedule_response

    def test_update_schedule_success(
        self, service, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        schedule_id = sample_schedule_model.id
        update_dto = ScheduleUpdate(name="Updated Schedule Name")
        service.repo.get_by_id.return_value = sample_schedule_model

        # Mock mapper functions
        with patch(
            "scheduler_api.services.schedule_service.apply_update"
        ) as mock_apply_update, patch(
            "scheduler_api.services.schedule_service.to_response"
        ) as mock_to_response:
            mock_apply_update.return_value = sample_schedule_model
            mock_to_response.return_value = sample_schedule_response

            # Test
            result = service.update_schedule(schedule_id, update_dto)

        # Verify
        service.repo.get_by_id.assert_called_once_with(schedule_id)
        mock_apply_update.assert_called_once_with(sample_schedule_model, update_dto)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()
        assert result == sample_schedule_response

    def test_update_schedule_not_found(self, service):
        # Setup
        schedule_id = uuid4()
        update_dto = ScheduleUpdate(name="Updated Schedule Name")
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.update_schedule(schedule_id, update_dto)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(schedule_id)
        service.session.commit.assert_not_called()  # No commit if not found
        service.session.flush.assert_not_called()  # No flush if not found

    def test_delete_schedule_success(self, service, sample_schedule_model):
        # Setup
        schedule_id = sample_schedule_model.id
        service.repo.get_by_id.return_value = sample_schedule_model
        service.repo.delete = MagicMock()

        # Test
        service.delete_schedule(schedule_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(schedule_id)
        service.repo.delete.assert_called_once_with(sample_schedule_model)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_delete_schedule_not_found(self, service):
        # Setup
        schedule_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        with pytest.raises(
            ValueError, match=f"Schedule with id {schedule_id} not found"
        ):
            service.delete_schedule(schedule_id)

        service.repo.get_by_id.assert_called_once_with(schedule_id)
        service.session.commit.assert_not_called()  # No commit if error
        service.session.flush.assert_not_called()  # No flush if error
