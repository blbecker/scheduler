"""Test ScheduleTemplateService with UnitOfWork pattern."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status

from scheduler_api.uow.unit_of_work import UnitOfWork
from scheduler_api.services.schedule_template_service import ScheduleTemplateService
from scheduler_api.schemas.schedule_template import (
    ScheduleTemplate,
    ScheduleTemplateUpdate,
    ScheduleTemplateResponse,
)


class TestScheduleTemplateService:
    """Test ScheduleTemplateService."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def sample_template_model(self):
        template = MagicMock()
        template.id = uuid4()
        template.name = "Weekly Schedule"
        template.created_at = datetime.utcnow()
        template.updated_at = datetime.utcnow()
        return template

    @pytest.fixture
    def sample_template_response(self, sample_template_model):
        return ScheduleTemplateResponse(
            id=sample_template_model.id,
            name=sample_template_model.name,
            created_at=sample_template_model.created_at,
            updated_at=sample_template_model.updated_at,
        )

    def test_list_schedule_templates(
        self, mock_uow, sample_template_model, sample_template_response
    ):
        # Setup
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = [sample_template_model]

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test
            result = service.list_schedule_templates()

        # Verify
        mock_repo.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == sample_template_response.id
        assert result[0].name == sample_template_response.name

    def test_get_schedule_template(
        self, mock_uow, sample_template_model, sample_template_response
    ):
        # Setup
        template_id = sample_template_model.id
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test
            result = service.get_schedule_template(template_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(template_id)
        assert result.id == sample_template_response.id
        assert result.name == sample_template_response.name

    def test_get_schedule_template_not_found(self, mock_uow):
        # Setup
        template_id = uuid4()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_schedule_template(template_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_create_schedule_template(
        self, mock_uow, sample_template_model, sample_template_response
    ):
        # Setup
        create_dto = ScheduleTemplate(name="Weekly Schedule")
        mock_repo = MagicMock()
        mock_repo.add.return_value = sample_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test
            result = service.create_schedule_template(create_dto)

        # Verify
        mock_repo.add.assert_called_once()
        mock_uow.flush.assert_called_once()
        assert result.id == sample_template_response.id
        assert result.name == sample_template_response.name

    def test_update_schedule_template(
        self, mock_uow, sample_template_model, sample_template_response
    ):
        # Setup
        template_id = sample_template_model.id
        update_dto = ScheduleTemplateUpdate(name="Updated Schedule")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_template_model
        mock_repo.add.return_value = sample_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test
            result = service.update_schedule_template(template_id, update_dto)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(template_id)
        mock_repo.add.assert_called_once()
        mock_uow.flush.assert_called_once()
        assert result.id == sample_template_response.id

    def test_update_schedule_template_not_found(self, mock_uow):
        # Setup
        template_id = uuid4()
        update_dto = ScheduleTemplateUpdate(name="Updated Schedule")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_schedule_template(template_id, update_dto)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_delete_schedule_template(self, mock_uow, sample_template_model):
        # Setup
        template_id = sample_template_model.id
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test
            service.delete_schedule_template(template_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(template_id)
        mock_repo.delete.assert_called_once_with(sample_template_model)

    def test_delete_schedule_template_not_found(self, mock_uow):
        # Setup
        template_id = uuid4()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.schedule_template_service.ScheduleTemplateRepository",
            return_value=mock_repo,
        ):
            service = ScheduleTemplateService(mock_uow)

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_schedule_template(template_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(template_id)
