"""Test WorkerService with simplified approach."""

import pytest
from unittest.mock import MagicMock, create_autospec, patch
from uuid import UUID, uuid4
from datetime import datetime, UTC
from sqlmodel import Session

from scheduler_api.services.worker_service import WorkerService
from scheduler_api.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse
from scheduler_api.db.models.core.worker import WorkerModel


class TestWorkerService:
    """Test WorkerService with simplified approach."""

    @pytest.fixture
    def mock_session(self):
        """Mock SQLModel session."""
        return create_autospec(Session)

    @pytest.fixture
    def service(self, mock_session):
        """WorkerService instance with mocked session."""
        return WorkerService(mock_session)

    @pytest.fixture
    def sample_worker_create(self):
        """Sample WorkerCreate DTO."""
        return WorkerCreate(name="Test Worker")

    @pytest.fixture
    def sample_worker_model(self):
        """Sample WorkerModel."""
        worker = MagicMock(spec=WorkerModel)
        worker.id = uuid4()
        worker.name = "Test Worker"
        worker.created_at = datetime.now(UTC)
        worker.updated_at = datetime.now(UTC)
        return worker

    @pytest.fixture
    def sample_worker_response(self, sample_worker_model):
        """Sample WorkerResponse DTO."""
        return WorkerResponse(
            id=sample_worker_model.id,
            name=sample_worker_model.name,
            created_at=sample_worker_model.created_at,
            updated_at=sample_worker_model.updated_at,
        )

    def test_service_initialization(self, mock_session):
        """Test that service initializes repository with session."""
        service = WorkerService(mock_session)
        assert service.session == mock_session
        assert hasattr(service, "repo")
        # Repository should be instantiated with the same session
        assert service.repo.session == mock_session

    def test_list_workers_success(self, service):
        """Test that list_workers works (no commit for read)."""
        # Mock repository
        mock_workers = [MagicMock(), MagicMock()]
        service.repo.get_all = MagicMock(return_value=mock_workers)

        # Mock mapper function
        with patch(
            "scheduler_api.services.worker_service.to_response"
        ) as mock_to_response:
            mock_responses = [
                MagicMock(spec=WorkerResponse),
                MagicMock(spec=WorkerResponse),
            ]
            mock_to_response.side_effect = lambda x: (
                mock_responses.pop(0) if mock_responses else MagicMock()
            )

            # Test
            result = service.list_workers()

        # Verify
        service.repo.get_all.assert_called_once()
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read

    def test_get_worker_found(self, service):
        """Test get_worker returns response when found (no commit for read)."""
        worker_id = uuid4()
        mock_worker = MagicMock()
        service.repo.get_by_id = MagicMock(return_value=mock_worker)

        with patch(
            "scheduler_api.services.worker_service.to_response"
        ) as mock_to_response:
            mock_response = MagicMock(spec=WorkerResponse)
            mock_to_response.return_value = mock_response

            result = service.get_worker(worker_id)

        service.repo.get_by_id.assert_called_once_with(worker_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert result == mock_response

    def test_get_worker_not_found(self, service):
        """Test get_worker returns None when not found (no commit for read)."""
        worker_id = uuid4()
        service.repo.get_by_id = MagicMock(return_value=None)

        result = service.get_worker(worker_id)

        service.repo.get_by_id.assert_called_once_with(worker_id)
        service.session.commit.assert_not_called()  # No commit for read
        service.session.flush.assert_not_called()  # No flush for read
        assert result is None

    def test_create_worker_success(self, service):
        """Test create_worker works with commit and flush."""
        # Mock repository and mapper
        mock_worker = MagicMock()
        mock_saved = MagicMock()

        with patch(
            "scheduler_api.services.worker_service.from_create"
        ) as mock_from_create, patch(
            "scheduler_api.services.worker_service.to_response"
        ) as mock_to_response:
            mock_from_create.return_value = mock_worker
            mock_to_response.return_value = MagicMock(spec=WorkerResponse)
            service.repo.add = MagicMock(return_value=mock_saved)

            # Test
            sample_dto = WorkerCreate(name="Test Worker")
            service.create_worker(sample_dto)

        # Verify
        mock_from_create.assert_called_once_with(sample_dto)
        service.repo.add.assert_called_once_with(mock_worker)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_update_worker_success(self, service):
        """Test update_worker works with commit and flush."""
        worker_id = uuid4()
        update_dto = WorkerUpdate(name="Updated Worker")
        mock_worker = MagicMock()

        with patch(
            "scheduler_api.services.worker_service.apply_update"
        ) as mock_apply_update, patch(
            "scheduler_api.services.worker_service.to_response"
        ) as mock_to_response:
            mock_apply_update.return_value = mock_worker
            mock_to_response.return_value = MagicMock(spec=WorkerResponse)
            service.repo.get_by_id = MagicMock(return_value=mock_worker)

            # Test
            service.update_worker(worker_id, update_dto)

        # Verify
        service.repo.get_by_id.assert_called_once_with(worker_id)
        mock_apply_update.assert_called_once_with(mock_worker, update_dto)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_update_worker_not_found(self, service):
        """Test update_worker returns None when not found (no commit)."""
        worker_id = uuid4()
        update_dto = WorkerUpdate(name="Updated Worker")
        service.repo.get_by_id = MagicMock(return_value=None)

        result = service.update_worker(worker_id, update_dto)

        service.repo.get_by_id.assert_called_once_with(worker_id)
        service.session.commit.assert_not_called()  # No commit if not found
        service.session.flush.assert_not_called()  # No flush if not found
        assert result is None

    def test_delete_worker_success(self, service):
        """Test delete_worker works with commit and flush."""
        worker_id = uuid4()
        mock_worker = MagicMock()
        service.repo.get_by_id = MagicMock(return_value=mock_worker)
        service.repo.delete = MagicMock()

        # Test
        service.delete_worker(worker_id)

        # Verify
        service.repo.get_by_id.assert_called_once_with(worker_id)
        service.repo.delete.assert_called_once_with(mock_worker)
        service.session.flush.assert_called_once()
        service.session.commit.assert_called_once()

    def test_delete_worker_not_found(self, service):
        """Test delete_worker raises ValueError when not found (no commit)."""
        worker_id = uuid4()
        service.repo.get_by_id = MagicMock(return_value=None)

        with pytest.raises(ValueError, match=f"Worker with id {worker_id} not found"):
            service.delete_worker(worker_id)

        service.repo.get_by_id.assert_called_once_with(worker_id)
        service.session.commit.assert_not_called()  # No commit if error
        service.session.flush.assert_not_called()  # No flush if error
