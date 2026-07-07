"""Unit tests for WorkerRepository."""
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
import pytest
from sqlmodel import Session

from scheduler_api.repositories.worker_repository import WorkerRepository


class TestWorkerRepository:
    """Test WorkerRepository data access methods."""

    @pytest.fixture
    def mock_session(self):
        """Mock SQLModel session."""
        session = Mock(spec=Session)
        session.exec = MagicMock()
        session.get = MagicMock()
        session.add = MagicMock()
        session.delete = MagicMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """WorkerRepository instance with mocked session."""
        return WorkerRepository(mock_session)

    @pytest.fixture
    def sample_worker(self):
        """Mock WorkerModel for testing."""
        worker = Mock()
        worker.id = uuid4()
        worker.name = "Test Worker"
        return worker

    @pytest.fixture
    def mock_worker_model(self):
        """Mock WorkerModel class."""
        with patch('scheduler_api.repositories.worker_repository.WorkerModel') as mock:
            yield mock

    def test_get_all(self, repository, mock_session, sample_worker, mock_worker_model):
        """Test get_all returns all workers."""
        # Arrange
        mock_select = Mock()
        with patch('scheduler_api.repositories.worker_repository.select', return_value=mock_select):
            mock_result = Mock()
            mock_result.all.return_value = [sample_worker]
            mock_session.exec.return_value = mock_result

            # Act
            result = repository.get_all()

            # Assert
            assert len(result) == 1
            assert result[0] == sample_worker
            mock_session.exec.assert_called_once_with(mock_select)

    def test_get_by_id_found(self, repository, mock_session, sample_worker, mock_worker_model):
        """Test get_by_id returns worker when found."""
        # Arrange
        mock_session.get.return_value = sample_worker

        # Act
        result = repository.get_by_id(sample_worker.id)

        # Assert
        assert result == sample_worker
        mock_session.get.assert_called_once_with(mock_worker_model, sample_worker.id)

    def test_get_by_id_not_found(self, repository, mock_session, mock_worker_model):
        """Test get_by_id returns None when worker not found."""
        # Arrange
        worker_id = uuid4()
        mock_session.get.return_value = None

        # Act
        result = repository.get_by_id(worker_id)

        # Assert
        assert result is None
        mock_session.get.assert_called_once_with(mock_worker_model, worker_id)

    def test_add(self, repository, mock_session, sample_worker):
        """Test add adds worker to session."""
        # Act
        result = repository.add(sample_worker)

        # Assert
        assert result == sample_worker
        mock_session.add.assert_called_once_with(sample_worker)
        # Note: No commit() call - service owns transaction boundaries

    def test_delete(self, repository, mock_session, sample_worker):
        """Test delete removes worker from session."""
        # Act
        repository.delete(sample_worker)

        # Assert
        mock_session.delete.assert_called_once_with(sample_worker)
        # Note: No commit() call - service owns transaction boundaries