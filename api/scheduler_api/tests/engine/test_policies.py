"""Shift-length policy resolution."""

from __future__ import annotations

from scheduler_api.engine.models.problem import ShiftLengthPolicy
from scheduler_api.engine.policies import (
    clamp_duration,
    effective_bounds,
    effective_preferred_bounds,
    fits_bounds,
)
from scheduler_api.tests.engine.builders import WORKER_1, make_worker


def test_policy_defaults_are_two_to_twelve_hours() -> None:
    policy = ShiftLengthPolicy()
    assert (policy.minimum_minutes, policy.maximum_minutes) == (120, 720)


def test_effective_bounds_use_policy_by_default() -> None:
    assert effective_bounds(make_worker(WORKER_1), ShiftLengthPolicy()) == (120, 720)


def test_per_worker_overrides_win_over_policy() -> None:
    worker = make_worker(WORKER_1, minimum_shift_minutes=240, maximum_shift_minutes=480)
    assert effective_bounds(worker, ShiftLengthPolicy()) == (240, 480)


def test_preferences_are_separate_from_hard_bounds_and_default_to_unset() -> None:
    worker = make_worker(WORKER_1)
    assert effective_preferred_bounds(worker, ShiftLengthPolicy()) == (None, None)


def test_preference_bounds_are_read_independently() -> None:
    worker = make_worker(WORKER_1, preferred_minimum_shift_minutes=300)
    assert effective_preferred_bounds(worker, ShiftLengthPolicy()) == (300, None)


def test_fits_bounds_includes_the_endpoints() -> None:
    assert fits_bounds(120, (120, 720))
    assert fits_bounds(720, (120, 720))
    assert not fits_bounds(119, (120, 720))
    assert not fits_bounds(721, (120, 720))


def test_clamp_duration_pulls_into_bounds() -> None:
    assert clamp_duration(60, (120, 720)) == 120
    assert clamp_duration(900, (120, 720)) == 720
    assert clamp_duration(300, (120, 720)) == 300


def test_policy_rejects_inverted_bounds() -> None:
    import pytest

    with pytest.raises(ValueError):
        ShiftLengthPolicy(minimum_minutes=600, maximum_minutes=300)
