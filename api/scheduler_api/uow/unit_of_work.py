import time
import logging
from sqlmodel import Session
from contextlib import AbstractContextManager
from typing import Optional

logger = logging.getLogger(__name__)


class UnitOfWork(AbstractContextManager):
    """
    Manages transaction boundaries for a SQLAlchemy session with logging and metrics.

    Provides a context manager that automatically commits on success or rolls back
    on exception. All transaction operations are logged at DEBUG level with timing
    metrics and operation counting.
    """

    def __init__(self, session: Session):
        """
        Initialize UnitOfWork with a SQLAlchemy session.

        Args:
            session: SQLAlchemy session to manage
        """
        self.session = session
        self._start_time: Optional[float] = None
        self._operation_count: int = 0

    def commit(self) -> None:
        """
        Commit the current transaction with logging and timing.

        Logs at DEBUG level with timing metrics and operation count.
        """
        logger.debug("Committing transaction")
        start = time.perf_counter()

        try:
            self.session.commit()
            duration = time.perf_counter() - start
            logger.debug(
                f"Transaction committed successfully in {duration:.3f}s, "
                f"operations: {self._operation_count}"
            )
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error(
                f"Transaction commit failed after {duration:.3f}s: {e}",
                exc_info=True,  # Include full stack trace at ERROR level
            )
            raise

    def rollback(self) -> None:
        """
        Rollback the current transaction with logging and timing.

        Logs at DEBUG level with timing metrics.
        """
        logger.debug("Rolling back transaction")
        start = time.perf_counter()

        try:
            self.session.rollback()
            duration = time.perf_counter() - start
            logger.debug(f"Transaction rolled back in {duration:.3f}s")
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error(
                f"Transaction rollback failed after {duration:.3f}s: {e}",
                exc_info=True,  # Include full stack trace at ERROR level
            )
            raise

    def flush(self) -> None:
        """
        Flush pending changes with logging and timing.

        Used for generating primary keys without committing the transaction.
        Logs at DEBUG level with timing metrics.
        """
        logger.debug("Flushing session")
        self._operation_count += 1  # Count flush as an operation
        start = time.perf_counter()

        try:
            self.session.flush()
            duration = time.perf_counter() - start
            logger.debug(f"Session flushed in {duration:.3f}s")
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error(
                f"Session flush failed after {duration:.3f}s: {e}",
                exc_info=True,  # Include full stack trace at ERROR level
            )
            raise

    def refresh(self, instance) -> None:
        """
        Refresh instance state with logging and timing.

        Logs at DEBUG level with timing metrics.

        Args:
            instance: SQLAlchemy model instance to refresh
        """
        logger.debug(f"Refreshing instance: {type(instance).__name__}")
        self._operation_count += 1  # Count refresh as an operation
        start = time.perf_counter()

        try:
            self.session.refresh(instance)
            duration = time.perf_counter() - start
            logger.debug(f"Instance refreshed in {duration:.3f}s")
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error(
                f"Instance refresh failed after {duration:.3f}s: {e}",
                exc_info=True,  # Include full stack trace at ERROR level
            )
            raise

    def __enter__(self):
        """
        Enter context manager with transaction start logging.

        Returns:
            UnitOfWork instance
        """
        self._start_time = time.perf_counter()
        self._operation_count = 0
        logger.debug("Transaction context entered")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager with transaction completion logging.

        Commits on success, rolls back on exception. Logs total duration
        and operation count.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self._start_time is None:
            return  # Context manager wasn't properly entered

        total_duration = time.perf_counter() - self._start_time

        if exc_type is not None:
            logger.debug(
                f"Transaction rolling back due to exception "
                f"after {total_duration:.3f}s"
            )
            self.rollback()
        else:
            logger.debug(
                f"Transaction committing after {total_duration:.3f}s, "
                f"total operations: {self._operation_count}"
            )
            self.commit()

        # Session closing is handled by FastAPI dependency, not UnitOfWork
