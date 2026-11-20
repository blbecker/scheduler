from __future__ import annotations

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator, model_validator

from .base import EngineModel


class TimeSlot(EngineModel):
    index: int = Field(ge=0)
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def _validate_interval(self) -> TimeSlot:
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValueError("slot start must be timezone-aware")
        if self.end.tzinfo is None or self.end.utcoffset() is None:
            raise ValueError("slot end must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("slot end must be after slot start")
        return self


class StaffingRequirement(EngineModel):
    job_id: UUID
    slot_index: int = Field(ge=0)
    required_workers: int = Field(ge=0)


class WorkerInfo(EngineModel):
    worker_id: UUID
    available_slot_indices: tuple[int, ...]
    qualified_job_ids: tuple[UUID, ...]
    minimum_shift_slots: int | None = Field(default=None, ge=1)
    maximum_shift_slots: int | None = Field(default=None, ge=1)

    @field_validator("available_slot_indices")
    @classmethod
    def _normalize_available(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(index < 0 for index in value):
            raise ValueError("available slot indices must be non-negative")
        return tuple(sorted(set(value)))

    @field_validator("qualified_job_ids")
    @classmethod
    def _normalize_qualified(cls, value: tuple[UUID, ...]) -> tuple[UUID, ...]:
        return tuple(sorted(set(value), key=lambda job_id: job_id.hex))

    @model_validator(mode="after")
    def _validate_shift_bounds(self) -> WorkerInfo:
        if (
            self.minimum_shift_slots is not None
            and self.maximum_shift_slots is not None
            and self.maximum_shift_slots < self.minimum_shift_slots
        ):
            raise ValueError("maximum_shift_slots must be >= minimum_shift_slots")
        return self


class JobInfo(EngineModel):
    job_id: UUID


class SchedulingProblem(EngineModel):
    timezone: str
    slots: tuple[TimeSlot, ...] = Field(min_length=1)
    staffing_requirements: tuple[StaffingRequirement, ...]
    workers: tuple[WorkerInfo, ...]
    jobs: tuple[JobInfo, ...]

    @field_validator("timezone")
    @classmethod
    def _validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"unknown timezone: {value}") from exc
        return value

    @model_validator(mode="after")
    def _validate_problem(self) -> SchedulingProblem:
        slot_count = len(self.slots)
        for position, slot in enumerate(self.slots):
            if slot.index != position:
                raise ValueError(
                    "slot indices must be exactly 0..len(slots)-1 in order"
                )
            if position + 1 < slot_count:
                following = self.slots[position + 1]
                if slot.end != following.start:
                    raise ValueError("adjacent slots must share contiguous instants")

        job_ids = [job.job_id for job in self.jobs]
        if len(job_ids) != len(set(job_ids)):
            raise ValueError("duplicate job IDs")
        known_jobs = set(job_ids)

        worker_ids = [worker.worker_id for worker in self.workers]
        if len(worker_ids) != len(set(worker_ids)):
            raise ValueError("duplicate worker IDs")

        demand_keys: set[tuple[UUID, int]] = set()
        for requirement in self.staffing_requirements:
            if requirement.slot_index >= slot_count:
                raise ValueError("staffing requirement references unknown slot")
            if requirement.job_id not in known_jobs:
                raise ValueError("staffing requirement references unknown job")
            key = (requirement.job_id, requirement.slot_index)
            if key in demand_keys:
                raise ValueError("duplicate staffing requirement")
            demand_keys.add(key)

        for worker in self.workers:
            for index in worker.available_slot_indices:
                if index >= slot_count:
                    raise ValueError("worker availability references unknown slot")
            for job_id in worker.qualified_job_ids:
                if job_id not in known_jobs:
                    raise ValueError("worker qualification references unknown job")

        return self

    @property
    def slot_count(self) -> int:
        return len(self.slots)
