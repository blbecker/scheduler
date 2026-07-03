"""Unit tests for UnitOfWork with mocked session."""

import pytest
import logging
from unittest.mock import MagicMock, patch
from uuid import uuid4

from scheduler_api.uow.unit_of_work import UnitOfWork


class TestUnitOfWork:
    """Test UnitOfWork with mocked SQLAlchemy session."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mocked SQLAlchemy session."""
        session = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()
        session.flush = MagicMock()
        session.refresh = MagicMock()
        return session
    
    @pytest.fixture
    def uow(self, mock_session):
        """Create UnitOfWork with mocked session."""
        return UnitOfWork(mock_session)
    
    def test_initialization(self, mock_session):
        """Test UnitOfWork initialization with session."""
        uow = UnitOfWork(mock_session)
        assert uow.session == mock_session
        assert uow._start_time is None
        assert uow._operation_count == 0
    
    def test_commit_with_logging(self, uow, mock_session, caplog):
        """Test commit logs transaction success with timing."""
        caplog.set_level(logging.DEBUG)
        
        uow.commit()
        
        # Verify session commit was called
        mock_session.commit.assert_called_once()
        
        # Verify logging
        assert "Committing transaction" in caplog.text
        assert "Transaction committed successfully" in caplog.text
    
    def test_rollback_with_logging(self, uow, mock_session, caplog):
        """Test rollback logs transaction rollback with timing."""
        caplog.set_level(logging.DEBUG)
        
        uow.rollback()
        
        # Verify session rollback was called
        mock_session.rollback.assert_called_once()
        
        # Verify logging
        assert "Rolling back transaction" in caplog.text
        assert "Transaction rolled back" in caplog.text
    
    def test_flush_with_logging_and_operation_count(self, uow, mock_session, caplog):
        """Test flush logs operation and increments operation count."""
        caplog.set_level(logging.DEBUG)
        
        initial_count = uow._operation_count
        uow.flush()
        
        # Verify session flush was called
        mock_session.flush.assert_called_once()
        
        # Verify operation count incremented
        assert uow._operation_count == initial_count + 1
        
        # Verify logging
        assert "Flushing session" in caplog.text
        assert "Session flushed" in caplog.text
    
    def test_refresh_with_logging_and_operation_count(self, uow, mock_session, caplog):
        """Test refresh logs operation and increments operation count."""
        caplog.set_level(logging.DEBUG)
        
        mock_instance = MagicMock()
        mock_instance.__class__.__name__ = "TestModel"
        
        initial_count = uow._operation_count
        uow.refresh(mock_instance)
        
        # Verify session refresh was called with correct instance
        mock_session.refresh.assert_called_once_with(mock_instance)
        
        # Verify operation count incremented
        assert uow._operation_count == initial_count + 1
        
        # Verify logging
        assert "Refreshing instance: TestModel" in caplog.text
        assert "Instance refreshed" in caplog.text
    
    def test_context_manager_success_commits(self, mock_session):
        """Test context manager commits on successful completion."""
        with UnitOfWork(mock_session) as uow:
            # Do some operations
            uow.flush()
            uow.flush()
        
        # Verify commit was called (not rollback)
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()
    
    def test_context_manager_exception_rolls_back(self, mock_session):
        """Test context manager rolls back on exception."""
        with pytest.raises(ValueError):
            with UnitOfWork(mock_session) as uow:
                uow.flush()
                raise ValueError("Test error")
        
        # Verify rollback was called (not commit)
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
    
    def test_context_manager_logs_total_duration(self, mock_session, caplog):
        """Test context manager logs total duration and operation count."""
        caplog.set_level(logging.DEBUG)
        
        with UnitOfWork(mock_session) as uow:
            uow.flush()
            uow.flush()
        
        # Verify logging includes duration and operation count
        assert "Transaction committing after" in caplog.text
        assert "total operations: 2" in caplog.text
    
    def test_context_manager_exception_logs_rollback(self, mock_session, caplog):
        """Test context manager logs rollback on exception."""
        caplog.set_level(logging.DEBUG)
        
        with pytest.raises(RuntimeError):
            with UnitOfWork(mock_session):
                raise RuntimeError("Forced error")
        
        # Verify rollback logging
        assert "rolling back due to exception" in caplog.text
    
    def test_commit_exception_logs_error_with_stack_trace(self, uow, mock_session, caplog):
        """Test commit failure logs error with stack trace."""
        caplog.set_level(logging.ERROR)
        
        # Make commit raise an exception
        error = ValueError("Commit failed")
        mock_session.commit.side_effect = error
        
        with pytest.raises(ValueError):
            uow.commit()
        
        # Verify error logging with stack trace
        assert "Transaction commit failed" in caplog.text
        assert "ValueError" in caplog.text
    
    def test_rollback_exception_logs_error_with_stack_trace(self, uow, mock_session, caplog):
        """Test rollback failure logs error with stack trace."""
        caplog.set_level(logging.ERROR)
        
        # Make rollback raise an exception
        error = RuntimeError("Rollback failed")
        mock_session.rollback.side_effect = error
        
        with pytest.raises(RuntimeError):
            uow.rollback()
        
        # Verify error logging with stack trace
        assert "Transaction rollback failed" in caplog.text
        assert "RuntimeError" in caplog.text
    
    def test_flush_exception_logs_error_with_stack_trace(self, uow, mock_session, caplog):
        """Test flush failure logs error with stack trace."""
        caplog.set_level(logging.ERROR)
        
        # Make flush raise an exception
        error = TypeError("Flush failed")
        mock_session.flush.side_effect = error
        
        with pytest.raises(TypeError):
            uow.flush()
        
        # Verify error logging with stack trace
        assert "Session flush failed" in caplog.text
        assert "TypeError" in caplog.text
    
    def test_refresh_exception_logs_error_with_stack_trace(self, uow, mock_session, caplog):
        """Test refresh failure logs error with stack trace."""
        caplog.set_level(logging.ERROR)
        
        mock_instance = MagicMock()
        
        # Make refresh raise an exception
        error = AttributeError("Refresh failed")
        mock_session.refresh.side_effect = error
        
        with pytest.raises(AttributeError):
            uow.refresh(mock_instance)
        
        # Verify error logging with stack trace
        assert "Instance refresh failed" in caplog.text
        assert "AttributeError" in caplog.text
    
    def test_operation_count_in_context_manager(self, mock_session):
        """Test operation count is reset in context manager."""
        with UnitOfWork(mock_session) as uow:
            assert uow._operation_count == 0
            uow.flush()
            assert uow._operation_count == 1
            uow.refresh(MagicMock())
            assert uow._operation_count == 2
        
        # New context should reset count
        with UnitOfWork(mock_session) as uow:
            assert uow._operation_count == 0