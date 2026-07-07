"""Test ShiftTemplateService with simplified approach."""

import pytest
from unittest.mock import MagicMock, create_autospec, patch
from uuid import uuid4
from datetime import datetime, UTC, time
from sqlmodel import Session

from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.schemas.shift_template import (
    ShiftTemplateCreate,
    ShiftTemplateUpdate,
    ShiftTemplateResponse,
)


class TestShiftTemplateService:
    """Test ShiftTemplateService with simplified approach."""

    @pytest.fixture
    def mock_session(self):
        """Mock SQLModel session."""
        return create_autospec(Session)

    @pytest.fixture
    def service(self, mock_session):
        """ShiftTemplateService instance with mocked session."""
        service = ShiftTemplateService(mock_session)
        service.repo = MagicMock()
        return service

    @pytest.fixture
    def sample_shift_template_model(self):
        template = MagicMock()
        template.id = uuid4()
        template.name = "Morning Shift"
        template.schedule_template_id = uuid4()
        template.start_time = time(9, 0, 0)
        template.end_time = time(17, 0, 0)
        template.created_at = datetime.now(UTC)
        template.updated_at = datetime.now(UTC)
        return template

    @pytest.fixture
    def sample_shift_template_response(self, sample_shift_template_model):
        return ShiftTemplateResponse(
            id=sample_shift_template_model.id,
            name=sample_shift_template_model.name,
            schedule_template_id=sample_shift_template_model.schedule_template_id,
            start_time=sample_shift_template_model.start_time,
            end_time=sample_shift_template_model.end_time,
            created_at=sample_shift_template_model.created_at,
            updated_at=sample_shift_template_model.updated_at,
        )

    def test_service_initialization(self, mock_session):
        """Test that service initializes repository with session."""
        service = ShiftTemplateService(mock_session)
        assert service.session == mock_session
        assert hasattr(service, "repo")
        # Repository should be instantiated with the same session
        assert service.repo.session == mock_session

    def test_list_shift_templates(
        self, service, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        service.repo.get_all.return_value = [sample_shift_template_model]

        # Mock mapper function
        with patch(
            "scheduler_api.services.shift_template_service.to_response"
        ) as mock_to_response:
            mock_responses = [sample_shift_template_response]
            mock_to_response.side_effect = lambda x: (
                mock_responses.pop(0) if mock_responses else MagicMock()
            )

            # Test
            result = service.list_shift_templates()

        # Verify
        service.repo.get_all.assert_called_once()
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert len(result) == 1

    def test_get_shift_template_found(
        self, service, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        template_id = sample_shift_template_model.id
        service.repo.get_by_id.return_value = sample_shift_template_model

        # Mock mapper function
        with patch(
            "scheduler_api.services.shift_template_service.to_response"
        ) as mock_to_response:
            mock_to_response.return_value = sample_shift_template_response

            # Test
            result = service.get_shift_template(template_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(template_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert result == sample_shift_template_response

    def test_get_shift_template_not_found(self, service):
        # Setup
        template_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.get_shift_template(template_id)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(template_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read

    def test_create_shift_template_success(
        self, service, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        create_dto = ShiftTemplateCreate(
            name="Morning Shift",
            schedule_template_id=sample_shift_template_model.schedule_template_id,
            start_time=time(9, 0, 0),
            end_time=time(17, 0, 0),
        )

        # Mock mapper functions
        with patch(
            "scheduler_api.services.shift_template_service.from_create"
        ) as mock_from_create, patch(
            "scheduler_api.services.shift_template_service.to_response"
        ) as mock_to_response:
            mock_from_create.return_value = sample_shift_template_model
            mock_to_response.return_value = sample_shift_template_response
            service.repo.add.return_value = sample_shift_template_model

            # Test
            result = service.create_shift_template(create_dto)

        # Verify
        mock_from_create.assert_called_once_with(create_dto)
        service.repo.add.assert_called_once_with(sample_shift_template_model)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()
        assert result == sample_shift_template_response

    def test_update_shift_template_success(
        self, service, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        template_id = sample_shift_template_model.id
        update_dto = ShiftTemplateUpdate(name="Updated Shift")
        service.repo.get_by_id.return_value = sample_shift_template_model

        # Mock mapper functions
        with patch(
            "scheduler_api.services.shift_template_service.apply_update"
        ) as mock_apply_update, patch(
            "scheduler_api.services.shift_template_service.to_response"
        ) as mock_to_response:
            mock_apply_update.return_value = sample_shift_template_model
            mock_to_response.return_value = sample_shift_template_response

            # Test
            result = service.update_shift_template(template_id, update_dto)

        # Verify
        service.repo.get_by_id.assert_called_once_with(template_id)
        mock_apply_update.assert_called_once_with(
            sample_shift_template_model, update_dto
        )
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()
        assert result == sample_shift_template_response

    def test_update_shift_template_not_found(self, service):
        # Setup
        template_id = uuid4()
        update_dto = ShiftTemplateUpdate(name="Updated Shift")
        service.repo.get_by_id.return_value = None

        # Test & Verify
        result = service.update_shift_template(template_id, update_dto)
        assert result is None
        service.repo.get_by_id.assert_called_once_with(template_id)
        service.session.commit.assert_not_called()  # No commit if not found
        service.session.flush.assert_not_called()  # No flush if not found

    def test_delete_shift_template_success(self, service, sample_shift_template_model):
        # Setup
        template_id = sample_shift_template_model.id
        service.repo.get_by_id.return_value = sample_shift_template_model
        service.repo.delete = MagicMock()

        # Test
        service.delete_shift_template(template_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(template_id)
        service.repo.delete.assert_called_once_with(sample_shift_template_model)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_delete_shift_template_not_found(self, service):
        # Setup
        template_id = uuid4()
        service.repo.get_by_id.return_value = None

        # Test & Verify
        with pytest.raises(
            ValueError, match=f"Shift template with id {template_id} not found"
        ):
            service.delete_shift_template(template_id)

        service.repo.get_by_id.assert_called_once_with(template_id)
        service.session.commit.assert_not_called()  # No commit if error
        service.session.flush.assert_not_called()  # No flush if error
