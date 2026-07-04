"""Test ShiftTemplateService with UnitOfWork pattern."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime, time
from fastapi import HTTPException, status

from scheduler_api.uow.unit_of_work import UnitOfWork
from scheduler_api.services.shift_template_service import ShiftTemplateService
from scheduler_api.schemas.shift_template import (
    ShiftTemplate,
    ShiftTemplateUpdate,
    ShiftTemplateResponse,
)


class TestShiftTemplateService:
    """Test ShiftTemplateService."""

    @pytest.fixture
    def mock_uow(self):
        uow = MagicMock(spec=UnitOfWork)
        uow.session = MagicMock()
        uow.flush = MagicMock()
        return uow

    @pytest.fixture
    def sample_shift_template_model(self):
        template = MagicMock()
        template.id = uuid4()
        template.name = "Morning Shift"
        template.schedule_template_id = uuid4()
        template.start_time = time(9, 0, 0)
        template.end_time = time(17, 0, 0)
        template.created_at = datetime.utcnow()
        template.updated_at = datetime.utcnow()
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

    def test_list_shift_templates(
        self, mock_uow, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        mock_repo = MagicMock()
        mock_repo.get_all.return_value = [sample_shift_template_model]

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test
            result = service.list_shift_templates()

        # Verify
        mock_repo.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == sample_shift_template_response.id
        assert result[0].name == sample_shift_template_response.name

    def test_get_shift_template(
        self, mock_uow, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        template_id = sample_shift_template_model.id
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_shift_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test
            result = service.get_shift_template(template_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(template_id)
        assert result.id == sample_shift_template_response.id
        assert result.name == sample_shift_template_response.name

    def test_get_shift_template_not_found(self, mock_uow):
        # Setup
        template_id = uuid4()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.get_shift_template(template_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_create_shift_template(
        self, mock_uow, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        create_dto = ShiftTemplate(
            name="Morning Shift",
            schedule_template_id=sample_shift_template_model.schedule_template_id,
            start_time=time(9, 0, 0),
            end_time=time(17, 0, 0),
        )
        mock_repo = MagicMock()
        mock_repo.add.return_value = sample_shift_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test
            result = service.create_shift_template(create_dto)

        # Verify
        mock_repo.add.assert_called_once()
        mock_uow.flush.assert_called_once()
        assert result.id == sample_shift_template_response.id
        assert result.name == sample_shift_template_response.name

    def test_update_shift_template(
        self, mock_uow, sample_shift_template_model, sample_shift_template_response
    ):
        # Setup
        template_id = sample_shift_template_model.id
        update_dto = ShiftTemplateUpdate(name="Updated Shift")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_shift_template_model
        mock_repo.add.return_value = sample_shift_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test
            result = service.update_shift_template(template_id, update_dto)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(template_id)
        mock_repo.add.assert_called_once()
        mock_uow.flush.assert_called_once()
        assert result.id == sample_shift_template_response.id

    def test_update_shift_template_not_found(self, mock_uow):
        # Setup
        template_id = uuid4()
        update_dto = ShiftTemplateUpdate(name="Updated Shift")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.update_shift_template(template_id, update_dto)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(template_id)

    def test_delete_shift_template(self, mock_uow, sample_shift_template_model):
        # Setup
        template_id = sample_shift_template_model.id
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_shift_template_model

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test
            service.delete_shift_template(template_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(template_id)
        mock_repo.delete.assert_called_once_with(sample_shift_template_model)

    def test_delete_shift_template_not_found(self, mock_uow):
        # Setup
        template_id = uuid4()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        # Patch the repository constructor to return our mock
        with patch(
            "scheduler_api.services.shift_template_service.ShiftTemplateRepository",
            return_value=mock_repo,
        ):
            service = ShiftTemplateService(mock_uow)

            # Test & Verify
            with pytest.raises(HTTPException) as exc_info:
                service.delete_shift_template(template_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(template_id)
