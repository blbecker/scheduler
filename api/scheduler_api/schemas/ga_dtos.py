from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ShiftAssignmentDTO(BaseModel):
    worker_id: UUID
    shift_id: UUID
    start_time: datetime
    end_time: datetime

    @validator("end_time")
    def validate_end_time_after_start_time(cls, v, values):
        if "start_time" in values and v < values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ScheduleDTO(BaseModel):
    id: UUID
    name: str
    assignments: List[ShiftAssignmentDTO] = Field(default_factory=list)
    fitness: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduleLayoutDTO(BaseModel):
    id: UUID
    name: str
    date_range_start: datetime
    date_range_end: datetime
    shift_templates: List[Dict[str, Any]] = Field(default_factory=list)
    worker_ids: List[UUID] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PopulationDTO(BaseModel):
    id: UUID
    generation: int = 0
    schedules: List[ScheduleDTO] = Field(default_factory=list)
    layout_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GAConfigDTO(BaseModel):
    population_size: int = Field(default=100, ge=10, le=1000)
    mutation_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    crossover_rate: float = Field(default=0.8, ge=0.0, le=1.0)
    elitism_count: int = Field(default=2, ge=0)
    max_generations: int = Field(default=100, ge=1, le=10000)


class GenerationResultDTO(BaseModel):
    best_schedule: ScheduleDTO
    fitness: float
    generation: int
    population_id: UUID
    completed_at: datetime = Field(default_factory=datetime.utcnow)
