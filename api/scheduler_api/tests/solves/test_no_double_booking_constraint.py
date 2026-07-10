"""Tests for no_double_booking_constraint module."""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timedelta

from scheduler_api.solves.schedule.constraints.no_double_booking_constraint import (
    NoDoubleBookingConstraint,
)
from scheduler_api.solves.schedule.genome import ScheduleGenome
from scheduler_api.solves.schedule.context import ScheduleSolveContext


class TestNoDoubleBookingConstraint:
    """Test the NoDoubleBookingConstraint class."""

    def test_constraint_initialization(self):
        """Test constraint initialization."""
        constraint = NoDoubleBookingConstraint()

        assert constraint.name == "no_double_booking_constraint"

    def test_validate_no_overlaps(self):
        """Test validation with no overlapping shifts."""
        constraint = NoDoubleBookingConstraint()

        # Create worker and shift IDs
        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()

        # Create non-overlapping times
        base_time = datetime(2024, 1, 1, 8, 0, 0)

        # Mock context
        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),  # 8am-12pm
            shift2_id: (
                base_time + timedelta(hours=5),
                base_time + timedelta(hours=9),
            ),  # 1pm-5pm
        }.get(shift_id)

        # Create genome with non-overlapping assignments
        genome = ScheduleGenome(
            assignments={shift1_id: [worker_id], shift2_id: [worker_id]}
        )

        result = constraint.validate(genome, mock_context)

        assert result is True
        assert mock_context.get_shift_times.call_count == 2

    def test_validate_with_overlaps(self):
        """Test validation with overlapping shifts."""
        constraint = NoDoubleBookingConstraint()

        # Create worker and shift IDs
        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()

        # Create overlapping times
        base_time = datetime(2024, 1, 1, 8, 0, 0)

        # Mock context
        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),  # 8am-12pm
            shift2_id: (
                base_time + timedelta(hours=3),
                base_time + timedelta(hours=7),
            ),  # 11am-3pm (overlaps!)
        }.get(shift_id)

        # Create genome with overlapping assignments
        genome = ScheduleGenome(
            assignments={shift1_id: [worker_id], shift2_id: [worker_id]}
        )

        result = constraint.validate(genome, mock_context)

        assert result is False  # Should detect overlap

    def test_validate_shift_without_times(self):
        """Test validation when shift has no time information."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()

        # Mock context - shift2 has no times
        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (datetime(2024, 1, 1, 8, 0, 0), datetime(2024, 1, 1, 12, 0, 0)),
            shift2_id: None,  # No time information
        }.get(shift_id)

        genome = ScheduleGenome(
            assignments={shift1_id: [worker_id], shift2_id: [worker_id]}
        )

        result = constraint.validate(genome, mock_context)

        # Should return True since shift2 is skipped
        assert result is True

    def test_validate_multiple_workers_no_overlaps(self):
        """Test validation with multiple workers, no overlaps."""
        constraint = NoDoubleBookingConstraint()

        worker1_id = uuid4()
        worker2_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),
            shift2_id: (base_time + timedelta(hours=5), base_time + timedelta(hours=9)),
        }.get(shift_id)

        # Worker1 has shift1, Worker2 has shift2 - no overlaps
        genome = ScheduleGenome(
            assignments={shift1_id: [worker1_id], shift2_id: [worker2_id]}
        )

        result = constraint.validate(genome, mock_context)

        assert result is True

    def test_validate_multiple_workers_with_overlaps(self):
        """Test validation with multiple workers, one has overlaps."""
        constraint = NoDoubleBookingConstraint()

        worker1_id = uuid4()
        worker2_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()
        shift3_id = uuid4()

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),  # 8am-12pm
            shift2_id: (
                base_time + timedelta(hours=5),
                base_time + timedelta(hours=9),
            ),  # 1pm-5pm
            shift3_id: (
                base_time + timedelta(hours=3),
                base_time + timedelta(hours=7),
            ),  # 11am-3pm
        }.get(shift_id)

        # Worker1 has non-overlapping shifts (1 & 2)
        # Worker2 has overlapping shifts (1 & 3)
        genome = ScheduleGenome(
            assignments={
                shift1_id: [worker1_id, worker2_id],
                shift2_id: [worker1_id],
                shift3_id: [worker2_id],
            }
        )

        result = constraint.validate(genome, mock_context)

        assert result is False  # Worker2 has overlapping shifts 1 and 3

    def test_penalty_no_overlaps(self):
        """Test penalty calculation with no overlaps."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        # Mock context with shift_schedule
        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True  # Has time information
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),
            shift2_id: (base_time + timedelta(hours=5), base_time + timedelta(hours=9)),
        }.get(shift_id)
        mock_context.worker_ids = [worker_id]
        mock_context.shift_ids = [shift1_id, shift2_id]

        genome = ScheduleGenome(
            assignments={shift1_id: [worker_id], shift2_id: [worker_id]}
        )

        penalty = constraint.penalty(genome, mock_context)

        assert penalty == 0.0  # No overlaps

    def test_penalty_with_overlaps(self):
        """Test penalty calculation with overlaps."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        # Mock context
        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),
            shift2_id: (base_time + timedelta(hours=3), base_time + timedelta(hours=7)),
        }.get(shift_id)
        mock_context.worker_ids = [worker_id]
        mock_context.shift_ids = [shift1_id, shift2_id]

        genome = ScheduleGenome(
            assignments={shift1_id: [worker_id], shift2_id: [worker_id]}
        )

        penalty = constraint.penalty(genome, mock_context)

        # 1 overlap / max_possible_overlaps(1 * (2-1) = 1) = 1.0
        assert penalty == 1.0

    def test_penalty_no_shift_schedule(self):
        """Test penalty when context has no shift schedule."""
        constraint = NoDoubleBookingConstraint()

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = False  # No time information

        genome = ScheduleGenome(assignments={})

        penalty = constraint.penalty(genome, mock_context)

        assert penalty == 0.0  # Can't check overlaps without schedule

    def test_penalty_shift_without_times(self):
        """Test penalty calculation when some shifts have no times."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()  # No times

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),
            shift2_id: None,  # No time information
        }.get(shift_id)
        mock_context.worker_ids = [worker_id]
        mock_context.shift_ids = [shift1_id, shift2_id]

        genome = ScheduleGenome(
            assignments={shift1_id: [worker_id], shift2_id: [worker_id]}
        )

        penalty = constraint.penalty(genome, mock_context)

        # Shift2 has no times, so no overlaps can be detected
        assert penalty == 0.0

    def test_penalty_multiple_overlaps(self):
        """Test penalty with multiple overlapping pairs."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()
        shift3_id = uuid4()

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        # All shifts overlap with each other
        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),
            shift2_id: (base_time + timedelta(hours=1), base_time + timedelta(hours=5)),
            shift3_id: (base_time + timedelta(hours=2), base_time + timedelta(hours=6)),
        }.get(shift_id)
        mock_context.worker_ids = [worker_id]
        mock_context.shift_ids = [shift1_id, shift2_id, shift3_id]

        # Worker assigned to all 3 overlapping shifts
        genome = ScheduleGenome(
            assignments={
                shift1_id: [worker_id],
                shift2_id: [worker_id],
                shift3_id: [worker_id],
            }
        )

        penalty = constraint.penalty(genome, mock_context)

        # With 3 shifts, max_possible_overlaps = 1 * (3-1) = 2
        # Overlap pairs: (1,2), (1,3), (2,3) = 3 overlaps
        # penalty = min(1.0, 3/2) = 1.0 (capped)
        assert penalty == 1.0

    def test_penalty_multiple_workers(self):
        """Test penalty with multiple workers, some with overlaps."""
        constraint = NoDoubleBookingConstraint()

        worker1_id = uuid4()
        worker2_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()
        shift3_id = uuid4()

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),
            shift2_id: (base_time + timedelta(hours=5), base_time + timedelta(hours=9)),
            shift3_id: (
                base_time + timedelta(hours=3),
                base_time + timedelta(hours=7),
            ),  # Overlaps with shift1
        }.get(shift_id)
        mock_context.worker_ids = [worker1_id, worker2_id]
        mock_context.shift_ids = [shift1_id, shift2_id, shift3_id]

        # Worker1: shift1 and shift2 (no overlap)
        # Worker2: shift1 and shift3 (overlap!)
        genome = ScheduleGenome(
            assignments={
                shift1_id: [worker1_id, worker2_id],
                shift2_id: [worker1_id],
                shift3_id: [worker2_id],
            }
        )

        penalty = constraint.penalty(genome, mock_context)

        # Max possible overlaps: 2 workers * (3-1) = 4
        # Actual overlaps: Worker2 has shift1 and shift3 overlapping = 1 overlap
        # penalty = min(1.0, 1/4) = 0.25
        assert penalty == 0.25

    def test_penalty_edge_cases(self):
        """Test penalty edge cases."""
        constraint = NoDoubleBookingConstraint()

        # Test with empty genome
        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True
        mock_context.worker_ids = []
        mock_context.shift_ids = []

        genome = ScheduleGenome(assignments={})

        penalty = constraint.penalty(genome, mock_context)

        assert penalty == 0.0

    def test_penalty_capped_at_one(self):
        """Test that penalty is capped at 1.0."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift_ids = [uuid4() for _ in range(5)]

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True
        mock_context.get_shift_times.side_effect = lambda shift_id: (
            base_time,
            base_time + timedelta(hours=1),
        )  # All shifts overlap

        mock_context.worker_ids = [worker_id]
        mock_context.shift_ids = shift_ids

        # Worker assigned to all shifts (all overlap)
        genome = ScheduleGenome(
            assignments={shift_id: [worker_id] for shift_id in shift_ids}
        )

        penalty = constraint.penalty(genome, mock_context)

        # Should be capped at 1.0
        assert penalty == 1.0

    def test_validate_back_to_back_shifts(self):
        """Test validation with back-to-back shifts (no overlap)."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift1_id = uuid4()
        shift2_id = uuid4()

        base_time = datetime(2024, 1, 1, 8, 0, 0)

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.get_shift_times.side_effect = lambda shift_id: {
            shift1_id: (base_time, base_time + timedelta(hours=4)),  # 8am-12pm
            shift2_id: (
                base_time + timedelta(hours=4),
                base_time + timedelta(hours=8),
            ),  # 12pm-4pm (exactly adjacent)
        }.get(shift_id)

        genome = ScheduleGenome(
            assignments={shift1_id: [worker_id], shift2_id: [worker_id]}
        )

        result = constraint.validate(genome, mock_context)

        # Back-to-back shifts (end time = start time) should not be considered overlapping
        assert result is True

    def test_penalty_with_single_shift(self):
        """Test penalty when worker has only one shift."""
        constraint = NoDoubleBookingConstraint()

        worker_id = uuid4()
        shift_id = uuid4()

        mock_context = Mock(spec=ScheduleSolveContext)
        mock_context.shift_schedule = True
        mock_context.get_shift_times.return_value = (
            datetime(2024, 1, 1, 8, 0, 0),
            datetime(2024, 1, 1, 12, 0, 0),
        )
        mock_context.worker_ids = [worker_id]
        mock_context.shift_ids = [shift_id]

        genome = ScheduleGenome(assignments={shift_id: [worker_id]})

        penalty = constraint.penalty(genome, mock_context)

        # Single shift can't overlap with anything
        assert penalty == 0.0
