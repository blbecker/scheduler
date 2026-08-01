"""DTOs for solve context and state management."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from .solve_components import SolvePhase


class ScheduleSolveContextDTO(BaseModel):
    """Serializable context for schedule solve with progress tracking."""

    template_id: str = Field(description="Template ID as string")
    shift_ids: list[str] = Field(
        default_factory=list, description="Shift IDs as strings"
    )
    worker_ids: list[str] = Field(
        default_factory=list, description="Worker IDs as strings"
    )
    skill_requirements: dict[str, list[str]] = Field(
        default_factory=dict, description="Shift ID -> list of skill IDs"
    )
    worker_skills: dict[str, list[str]] = Field(
        default_factory=dict, description="Worker ID -> list of skill IDs"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Solve parameters"
    )

    # Progress tracking
    phase: SolvePhase = Field(
        default=SolvePhase.PENDING, description="Current solve phase"
    )
    generation: int = Field(default=0, description="Current generation number")
    start_time: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Start time as ISO string",
    )
    best_fitness: float = Field(default=0.0, description="Best fitness so far")
    progress_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional progress metadata"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "template_id": "123e4567-e89b-12d3-a456-426614174000",
                "shift_ids": ["shift-1", "shift-2"],
                "worker_ids": ["worker-1", "worker-2"],
                "skill_requirements": {"shift-1": ["skill-a"]},
                "worker_skills": {"worker-1": ["skill-a"]},
                "parameters": {"population_size": 50, "max_generations": 100},
                "phase": "pending",
                "generation": 0,
                "start_time": "2024-01-01T00:00:00",
                "best_fitness": 0.0,
                "progress_metadata": {},
            }
        }
    )

    def update_progress(
        self, phase: SolvePhase, generation: int, best_fitness: float
    ) -> None:
        """Update progress tracking fields."""
        self.phase = phase
        self.generation = generation
        self.best_fitness = best_fitness
        self.progress_metadata["last_updated"] = datetime.utcnow().isoformat()
