"""Schemas for solve framework."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional
from uuid import UUID
from datetime import datetime


class ScheduleSolveParameters(BaseModel):
    """Parameters for schedule solve."""

    population_size: int = Field(
        default=50, ge=5, le=1000, description="Size of population"
    )
    max_generations: int = Field(
        default=100, ge=1, le=10000, description="Maximum generations"
    )
    mutation_rate: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Mutation probability"
    )
    selection_top_n: int = Field(
        default=25, ge=1, le=1000, description="Top N to select"
    )
    elite_size: int = Field(
        default=1, ge=0, le=100, description="Number of elites to preserve"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "population_size": 10,
                "max_generations": 20,
                "mutation_rate": 0.1,
                "selection_top_n": 5,
                "elite_size": 1,
            }
        }
    )


class ScheduleSolveRequest(BaseModel):
    """Request to create a schedule solve."""

    template_id: UUID = Field(description="ID of the schedule template to solve for")
    parameters: ScheduleSolveParameters


class ScheduleSolveCreateResponse(BaseModel):
    """Response for schedule solve creation."""

    id: UUID
    status: str = Field(
        default="pending", description="pending, queued, running, completed, failed"
    )
    template_id: UUID
    parameters: ScheduleSolveParameters
    schedule_solve_id: UUID = Field(
        description="ID of the persisted ScheduleSolveModel record"
    )


class ScheduleSolveStatus(BaseModel):
    """Response for schedule solve status."""

    id: UUID
    status: str = Field(description="pending, running, completed, failed")
    template_id: UUID
    parameters: ScheduleSolveParameters
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    current_generation: Optional[int] = None
    best_fitness: Optional[float] = None
    progress: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Progress 0-1"
    )
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None


class ScheduleSolveResult(BaseModel):
    """Response for schedule solve result."""

    id: UUID
    status: str = Field(description="completed, failed")
    best_genome: Optional[dict[str, Any]] = None
    best_fitness: float = Field(description="Fitness score of best genome (0.0-1.0)")
    generations: int = Field(description="Number of generations executed")
    elapsed_time: float = Field(description="Time taken in seconds")
    metrics: dict[str, Any] = Field(
        default_factory=dict, description="Additional solve metrics"
    )
    created_at: datetime
