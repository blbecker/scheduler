"""Test ScheduleService with repository pattern."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime, UTC
from fastapi import HTTPException, status

from scheduler_api.services.schedule_service import ScheduleService
from scheduler_api.schemas.schedule_crud import (
    Schedule,
    ScheduleUpdate,
    ScheduleResponse,
)


class TestScheduleService:
    """Test ScheduleService."""

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

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

    def test_list_schedules(
        self, mock_repo, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        mock_repo.get_all.return_value = [sample_schedule_model]
        service = ScheduleService(mock_repo)

        # Test
        result = service.list_schedules()

        # Verify
        mock_repo.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == sample_schedule_response.id
        assert result[0].name == sample_schedule_response.name

    def test_get_schedule(
        self, mock_repo, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        schedule_id = sample_schedule_model.id
        mock_repo.get_by_id.return_value = sample_schedule_model
        service = ScheduleService(mock_repo)

        # Test
        result = service.get_schedule(schedule_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
        assert result.id == sample_schedule_response.id
        assert result.name == sample_schedule_response.name

    def test_get_schedule_not_found(self, mock_repo):
        # Setup
        schedule_id = uuid4()
        mock_repo.get_by_id.return_value = None
        service = ScheduleService(mock_repo)

        # Test & Verify
        with pytest.raises(HTTPException) as exc_info:
            service.get_schedule(schedule_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(schedule_id)

    def test_create_schedule(
        self, mock_repo, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        create_dto = Schedule(
            name="January 2024 Schedule",
            schedule_template_id=sample_schedule_model.schedule_template_id,
        )
        mock_repo.add.return_value = sample_schedule_model
        
        # Mock the mapper function
        with patch(
            "scheduler_api.services.schedule_service.from_create",
            return_value=sample_schedule_model
        ), patch(
            "scheduler_api.services.schedule_service.to_response",
            return_value=sample_schedule_response
        ):
            service = ScheduleService(mock_repo)

            # Test
            result = service.create_schedule(create_dto)

        # Verify
        mock_repo.add.assert_called_once_with(sample_schedule_model)
        assert result.id == sample_schedule_response.id
        assert result.name == sample_schedule_response.name

    def test_update_schedule(
        self, mock_repo, sample_schedule_model, sample_schedule_response
    ):
        # Setup
        schedule_id = sample_schedule_model.id
        update_dto = ScheduleUpdate(name="Updated Schedule")
        mock_repo.get_by_id.return_value = sample_schedule_model
        mock_repo.add.return_value = sample_schedule_model
        service = ScheduleService(mock_repo)

        # Test
        result = service.update_schedule(schedule_id, update_dto)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
        mock_repo.add.assert_called_once()
        assert result.id == sample_schedule_response.id

    def test_update_schedule_not_found(self, mock_repo):
        # Setup
        schedule_id = uuid4()
        update_dto = ScheduleUpdate(name="Updated Schedule")
        mock_repo.get_by_id.return_value = None
        service = ScheduleService(mock_repo)

        # Test & Verify
        with pytest.raises(HTTPException) as exc_info:
            service.update_schedule(schedule_id, update_dto)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(schedule_id)

    def test_delete_schedule(self, mock_repo, sample_schedule_model):
        # Setup
        schedule_id = sample_schedule_model.id
        mock_repo.get_by_id.return_value = sample_schedule_model
        service = ScheduleService(mock_repo)

        # Test
        service.delete_schedule(schedule_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
        mock_repo.delete.assert_called_once_with(sample_schedule_model)

    def test_delete_schedule_not_found(self, mock_repo):
        # Setup
        schedule_id = uuid4()
        mock_repo.get_by_id.return_value = None
        service = ScheduleService(mock_repo)

        # Test & Verify
        with pytest.raises(HTTPException) as exc_info:
            service.delete_schedule(schedule_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(schedule_id)
