"""Test repository implementations."""

import pytest
from unittest.mock import MagicMock, create_autospec
from uuid import UUID, uuid4
from datetime import datetime, time
from sqlmodel import Session, select

from scheduler_api.repositories.schedule_template_repository import (
    ScheduleTemplateRepository,
)
from scheduler_api.repositories.shift_template_repository import ShiftTemplateRepository
from scheduler_api.repositories.schedule_repository import ScheduleRepository
from scheduler_api.repositories.schedule_solve_repository import ScheduleSolveRepository


class TestScheduleTemplateRepository:
    """Test ScheduleTemplateRepository."""

    @pytest.fixture
    def mock_session(self):
        return create_autospec(Session)

    @pytest.fixture
    def repository(self, mock_session):
        return ScheduleTemplateRepository(mock_session)

    @pytest.fixture
    def sample_schedule_template(self):
        # Use MagicMock to avoid SQLAlchemy relationship resolution issues
        template = MagicMock()
        template.id = uuid4()
        template.name = "Weekly Schedule"
        template.created_at = datetime.utcnow()
        template.updated_at = datetime.utcnow()
        return template

    def test_get_all(self, repository, mock_session, sample_schedule_template):
        # Setup
        mock_session.exec.return_value.all.return_value = [sample_schedule_template]

        # Test
        result = repository.get_all()

        # Verify
        mock_session.exec.assert_called_once()
        assert len(result) == 1
        assert result[0] == sample_schedule_template

    def test_get_by_id(self, repository, mock_session, sample_schedule_template):
        # Setup
        template_id = sample_schedule_template.id
        mock_session.get.return_value = sample_schedule_template

        # Test
        result = repository.get_by_id(template_id)

        # Verify
        mock_session.get.assert_called_once()
        # Check that get was called with some arguments (we can't easily check the exact model class)
        assert len(mock_session.get.call_args[0]) >= 1
        assert mock_session.get.call_args[0][1] == template_id
        assert result == sample_schedule_template

    def test_get_by_id_not_found(self, repository, mock_session):
        # Setup
        template_id = uuid4()
        mock_session.get.return_value = None

        # Test
        result = repository.get_by_id(template_id)

        # Verify
        mock_session.get.assert_called_once()
        assert result is None

    def test_add(self, repository, mock_session, sample_schedule_template):
        # Setup
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Test
        result = repository.add(sample_schedule_template)

        # Verify
        mock_session.add.assert_called_once_with(sample_schedule_template)
        # commit() and refresh() are now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()
        # mock_session.refresh.assert_called_once_with(sample_schedule_template)
        assert result == sample_schedule_template

    def test_delete(self, repository, mock_session, sample_schedule_template):
        # Setup
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        # Test
        repository.delete(sample_schedule_template)

        # Verify
        mock_session.delete.assert_called_once_with(sample_schedule_template)
        # commit() is now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()


class TestShiftTemplateRepository:
    """Test ShiftTemplateRepository."""

    @pytest.fixture
    def mock_session(self):
        return create_autospec(Session)

    @pytest.fixture
    def repository(self, mock_session):
        return ShiftTemplateRepository(mock_session)

    @pytest.fixture
    def sample_shift_template(self):
        # Use MagicMock to avoid SQLAlchemy relationship resolution issues
        template = MagicMock()
        template.id = uuid4()
        template.name = "Morning Shift"
        template.schedule_template_id = uuid4()
        template.start_time = time(9, 0, 0)
        template.end_time = time(17, 0, 0)
        template.created_at = datetime.utcnow()
        template.updated_at = datetime.utcnow()
        return template

    def test_get_all(self, repository, mock_session, sample_shift_template):
        # Setup
        mock_session.exec.return_value.all.return_value = [sample_shift_template]

        # Test
        result = repository.get_all()

        # Verify
        mock_session.exec.assert_called_once()
        assert len(result) == 1
        assert result[0] == sample_shift_template

    def test_get_by_id(self, repository, mock_session, sample_shift_template):
        # Setup
        template_id = sample_shift_template.id
        mock_session.get.return_value = sample_shift_template

        # Test
        result = repository.get_by_id(template_id)

        # Verify
        mock_session.get.assert_called_once()
        assert result == sample_shift_template

    def test_get_by_id_not_found(self, repository, mock_session):
        # Setup
        template_id = uuid4()
        mock_session.get.return_value = None

        # Test
        result = repository.get_by_id(template_id)

        # Verify
        mock_session.get.assert_called_once()
        assert result is None

    def test_add(self, repository, mock_session, sample_shift_template):
        # Setup
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Test
        result = repository.add(sample_shift_template)

        # Verify
        mock_session.add.assert_called_once_with(sample_shift_template)
        # commit() and refresh() are now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()
        # mock_session.refresh.assert_called_once_with(sample_shift_template)
        assert result == sample_shift_template

    def test_delete(self, repository, mock_session, sample_shift_template):
        # Setup
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        # Test
        repository.delete(sample_shift_template)

        # Verify
        mock_session.delete.assert_called_once_with(sample_shift_template)
        # commit() is now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()


class TestScheduleRepository:
    """Test ScheduleRepository."""

    @pytest.fixture
    def mock_session(self):
        return create_autospec(Session)

    @pytest.fixture
    def repository(self, mock_session):
        return ScheduleRepository(mock_session)

    @pytest.fixture
    def sample_schedule(self):
        # Use MagicMock to avoid SQLAlchemy relationship resolution issues
        schedule = MagicMock()
        schedule.id = uuid4()
        schedule.name = "January 2024 Schedule"
        schedule.schedule_template_id = uuid4()
        schedule.created_at = datetime.utcnow()
        schedule.updated_at = datetime.utcnow()
        return schedule

    def test_get_all(self, repository, mock_session, sample_schedule):
        # Setup
        mock_session.exec.return_value.all.return_value = [sample_schedule]

        # Test
        result = repository.get_all()

        # Verify
        mock_session.exec.assert_called_once()
        assert len(result) == 1
        assert result[0] == sample_schedule

    def test_get_by_id(self, repository, mock_session, sample_schedule):
        # Setup
        schedule_id = sample_schedule.id
        mock_session.get.return_value = sample_schedule

        # Test
        result = repository.get_by_id(schedule_id)

        # Verify
        mock_session.get.assert_called_once()
        assert result == sample_schedule

    def test_get_by_id_not_found(self, repository, mock_session):
        # Setup
        schedule_id = uuid4()
        mock_session.get.return_value = None

        # Test
        result = repository.get_by_id(schedule_id)

        # Verify
        mock_session.get.assert_called_once()
        assert result is None

    def test_add(self, repository, mock_session, sample_schedule):
        # Setup
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Test
        result = repository.add(sample_schedule)

        # Verify
        mock_session.add.assert_called_once_with(sample_schedule)
        # commit() and refresh() are now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()
        # mock_session.refresh.assert_called_once_with(sample_schedule)
        assert result == sample_schedule

    def test_delete(self, repository, mock_session, sample_schedule):
        # Setup
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        # Test
        repository.delete(sample_schedule)

        # Verify
        mock_session.delete.assert_called_once_with(sample_schedule)
        # commit() is now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()


class TestScheduleSolveRepository:
    """Test ScheduleSolveRepository."""

    @pytest.fixture
    def mock_session(self):
        return create_autospec(Session)

    @pytest.fixture
    def repository(self, mock_session):
        return ScheduleSolveRepository(mock_session)

    @pytest.fixture
    def sample_run(self):
        # Use MagicMock to avoid SQLAlchemy relationship resolution issues
        run = MagicMock()
        run.id = uuid4()
        run.schedule_template_id = uuid4()
        run.schedule_id = None
        run.status = "pending"
        run.started_at = None
        run.finished_at = None
        run.parameters = {}
        run.created_at = datetime.utcnow()
        run.updated_at = datetime.utcnow()
        return run

    def test_get_all(self, repository, mock_session, sample_run):
        # Setup
        mock_session.exec.return_value.all.return_value = [sample_run]

        # Test
        result = repository.get_all()

        # Verify
        mock_session.exec.assert_called_once()
        assert len(result) == 1
        assert result[0] == sample_run

    def test_get_by_id(self, repository, mock_session, sample_run):
        # Setup
        run_id = sample_run.id
        mock_session.get.return_value = sample_run

        # Test
        result = repository.get_by_id(run_id)

        # Verify
        mock_session.get.assert_called_once()
        assert result == sample_run

    def test_get_by_id_not_found(self, repository, mock_session):
        # Setup
        run_id = uuid4()
        mock_session.get.return_value = None

        # Test
        result = repository.get_by_id(run_id)

        # Verify
        mock_session.get.assert_called_once()
        assert result is None

    def test_add(self, repository, mock_session, sample_run):
        # Setup
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Test
        result = repository.add(sample_run)

        # Verify
        mock_session.add.assert_called_once_with(sample_run)
        # commit() and refresh() are now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()
        # mock_session.refresh.assert_called_once_with(sample_run)
        assert result == sample_run

    def test_delete(self, repository, mock_session, sample_run):
        # Setup
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        # Test
        repository.delete(sample_run)

        # Verify
        mock_session.delete.assert_called_once_with(sample_run)
        # commit() is now handled by UnitOfWork, not repositories
        # mock_session.commit.assert_called_once()
