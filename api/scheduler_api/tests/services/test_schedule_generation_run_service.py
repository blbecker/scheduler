"""Test ScheduleGenerationRunService with repository pattern."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime, UTC
from fastapi import HTTPException, status

from scheduler_api.services.schedule_generation_run_service import (
    ScheduleGenerationRunService,
)
from scheduler_api.schemas.schedule_generation_run import (
    ScheduleGenerationRun,
    ScheduleGenerationRunUpdate,
    ScheduleGenerationRunResponse,
)
from scheduler_api.db.models.enums import ScheduleGenerationStatus


class TestScheduleGenerationRunService:
    """Test ScheduleGenerationRunService."""

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_all = MagicMock()
        repo.get_by_id = MagicMock()
        repo.add = MagicMock()
        repo.delete = MagicMock()
        return repo

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

    def test_list_schedule_generation_runs(
        self, mock_repo, sample_run_model, sample_run_response
    ):
        # Setup
        mock_repo.get_all.return_value = [sample_run_model]
        service = ScheduleGenerationRunService(mock_repo)

        # Test
        result = service.list_schedule_generation_runs()

        # Verify
        mock_repo.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == sample_run_response.id
        assert result[0].status == sample_run_response.status

    def test_get_schedule_generation_run(
        self, mock_repo, sample_run_model, sample_run_response
    ):
        # Setup
        run_id = sample_run_model.id
        mock_repo.get_by_id.return_value = sample_run_model
        service = ScheduleGenerationRunService(mock_repo)

        # Test
        result = service.get_schedule_generation_run(run_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(run_id)
        assert result.id == sample_run_response.id
        assert result.status == sample_run_response.status

    def test_get_schedule_generation_run_not_found(self, mock_repo):
        # Setup
        run_id = uuid4()
        mock_repo.get_by_id.return_value = None
        service = ScheduleGenerationRunService(mock_repo)

        # Test & Verify
        with pytest.raises(HTTPException) as exc_info:
            service.get_schedule_generation_run(run_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(run_id)

    def test_create_schedule_generation_run(
        self, mock_repo, sample_run_model, sample_run_response
    ):
        # Setup
        create_dto = ScheduleGenerationRun(
            schedule_template_id=sample_run_model.schedule_template_id, parameters={}
        )
        mock_repo.add.return_value = sample_run_model
        
        # Mock the mapper function
        with patch(
            "scheduler_api.services.schedule_generation_run_service.from_create",
            return_value=sample_run_model
        ), patch(
            "scheduler_api.services.schedule_generation_run_service.to_response",
            return_value=sample_run_response
        ):
            service = ScheduleGenerationRunService(mock_repo)

            # Test
            result = service.create_schedule_generation_run(create_dto)

        # Verify
        mock_repo.add.assert_called_once_with(sample_run_model)
        assert result.id == sample_run_response.id
        assert result.status == sample_run_response.status

    def test_update_schedule_generation_run(
        self, mock_repo, sample_run_model, sample_run_response
    ):
        # Setup
        run_id = sample_run_model.id
        update_dto = ScheduleGenerationRunUpdate(
            status=ScheduleGenerationStatus.running
        )
        mock_repo.get_by_id.return_value = sample_run_model
        mock_repo.add.return_value = sample_run_model
        
        # Mock the mapper function
        with patch(
            "scheduler_api.services.schedule_generation_run_service.apply_update",
            return_value=sample_run_model
        ), patch(
            "scheduler_api.services.schedule_generation_run_service.to_response",
            return_value=sample_run_response
        ):
            service = ScheduleGenerationRunService(mock_repo)

            # Test
            result = service.update_schedule_generation_run(run_id, update_dto)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(run_id)
        mock_repo.add.assert_called_once_with(sample_run_model)
        assert result.id == sample_run_response.id

    def test_update_schedule_generation_run_not_found(self, mock_repo):
        # Setup
        run_id = uuid4()
        update_dto = ScheduleGenerationRunUpdate(
            status=ScheduleGenerationStatus.running
        )
        mock_repo.get_by_id.return_value = None
        service = ScheduleGenerationRunService(mock_repo)

        # Test & Verify
        with pytest.raises(HTTPException) as exc_info:
            service.update_schedule_generation_run(run_id, update_dto)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(run_id)

    def test_delete_schedule_generation_run(self, mock_repo, sample_run_model):
        # Setup
        run_id = sample_run_model.id
        mock_repo.get_by_id.return_value = sample_run_model
        service = ScheduleGenerationRunService(mock_repo)

        # Test
        service.delete_schedule_generation_run(run_id)

        # Verify
        mock_repo.get_by_id.assert_called_once_with(run_id)
        mock_repo.delete.assert_called_once_with(sample_run_model)

    def test_delete_schedule_generation_run_not_found(self, mock_repo):
        # Setup
        run_id = uuid4()
        mock_repo.get_by_id.return_value = None
        service = ScheduleGenerationRunService(mock_repo)

        # Test & Verify
        with pytest.raises(HTTPException) as exc_info:
            service.delete_schedule_generation_run(run_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        mock_repo.get_by_id.assert_called_once_with(run_id)
