"""Schedule limits scorer: organization caps on hours per week and shifts per day."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from uuid import UUID

from scheduler_api.engine.components.scorers._common import percentage, resolve_worker
from scheduler_api.engine.intervals import minutes_by_local_date
from scheduler_api.engine.models.component_io import (
    ScheduleLimitsScoreInput,
    ScheduleLimitsScoreResult,
)
from scheduler_api.engine.models.scores import Violation, ViolationCode


class ScheduleLimitsScorer:
    """Checks weekly hours and daily shift counts against configured caps.

    Both caps are nullable; when neither is configured every candidate scores 100.
    A shift is attributed to the local date on which it starts, and hours are
    measured as overlapped minutes, so a shift crossing midnight contributes to
    both dates while counting as one shift on its start date.
    """

    component_id = "schedule_limits"

    def score(self, input: ScheduleLimitsScoreInput) -> ScheduleLimitsScoreResult:
        problem = input.problem
        limits = problem.limits
        timezone = problem.tz
        scores: dict[UUID, float] = {}
        violations: dict[UUID, tuple[Violation, ...]] = {}
        for individual in input.individuals:
            minutes_per_week: dict[UUID, dict[tuple[int, int], int]] = defaultdict(
                lambda: defaultdict(int)
            )
            shifts_per_day: dict[UUID, dict[date, int]] = defaultdict(
                lambda: defaultdict(int)
            )
            found: list[Violation] = []
            for shift in individual.shifts:
                if resolve_worker(problem, shift) is None:
                    continue
                per_date = minutes_by_local_date(shift.start, shift.end, timezone)
                for local_day, minutes in per_date.items():
                    iso = local_day.isocalendar()
                    minutes_per_week[shift.worker_id][(iso.year, iso.week)] += minutes
                start_day = shift.start.astimezone(timezone).date()
                shifts_per_day[shift.worker_id][start_day] += 1

            checks = 0
            passed = 0
            for worker_id, weeks in minutes_per_week.items():
                if limits.maximum_hours_per_week is None:
                    continue
                cap = limits.maximum_hours_per_week * 60
                for (year, week), minutes in sorted(weeks.items()):
                    checks += 1
                    if minutes <= cap:
                        passed += 1
                        continue
                    found.append(
                        Violation(
                            code=ViolationCode.WEEKLY_HOURS_EXCEEDED,
                            worker_id=worker_id,
                            detail=(
                                f"{minutes} minutes in ISO week {year}-W{week:02d} "
                                f"exceeds the {cap}-minute cap"
                            ),
                        )
                    )
            for worker_id, days in shifts_per_day.items():
                if limits.maximum_shifts_per_day is None:
                    continue
                for local_day, count in sorted(days.items()):
                    checks += 1
                    if count <= limits.maximum_shifts_per_day:
                        passed += 1
                        continue
                    found.append(
                        Violation(
                            code=ViolationCode.SHIFTS_PER_DAY_EXCEEDED,
                            worker_id=worker_id,
                            detail=(
                                f"{count} shifts on {local_day} exceeds the cap of "
                                f"{limits.maximum_shifts_per_day}"
                            ),
                        )
                    )
            scores[individual.id] = percentage(passed, checks)
            violations[individual.id] = tuple(found)
        return ScheduleLimitsScoreResult(scores=scores, violations=violations)
