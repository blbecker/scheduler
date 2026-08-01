"""DTOs for population and candidate serialization."""

from typing import Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class CandidateDTO(BaseModel):
    """Serializable candidate representation for Redis storage."""

    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Candidate ID as string"
    )
    genome_data: dict[str, Any] = Field(description="Serialized genome representation")
    fitness: float = Field(default=0.0, description="Candidate fitness score")
    generation: int = Field(default=0, description="Generation number")
    score_breakdown: dict[str, float] = Field(
        default_factory=dict, description="Breakdown of scores by component"
    )
    parent_ids: list[str] = Field(
        default_factory=list, description="Parent candidate IDs"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "genome_data": {"assignments": [{"shift_id": "s1", "worker_id": "w1"}]},
                "fitness": 0.85,
                "generation": 5,
                "score_breakdown": {"skills_match_scorer": 0.9},
                "parent_ids": ["parent-1", "parent-2"],
                "metadata": {"type": "elite"},
            }
        }
    )


class PopulationDTO(BaseModel):
    """Serializable population representation for Redis storage."""

    generation: int = Field(description="Current generation number")
    candidates: list[CandidateDTO] = Field(
        default_factory=list, description="List of candidates in population"
    )

    @property
    def size(self) -> int:
        """Get population size."""
        return len(self.candidates)

    def get_top_n(self, n: int) -> list[CandidateDTO]:
        """Get top N candidates by fitness."""
        sorted_candidates = sorted(
            self.candidates, key=lambda c: c.fitness, reverse=True
        )
        return sorted_candidates[: min(n, len(sorted_candidates))]

    def get_best_fitness(self) -> float:
        """Get best fitness in population."""
        if not self.candidates:
            return 0.0
        return max(c.fitness for c in self.candidates)

    def get_average_fitness(self) -> float:
        """Get average fitness of population."""
        if not self.candidates:
            return 0.0
        return sum(c.fitness for c in self.candidates) / len(self.candidates)

    def model_dump_json(self) -> str:
        """JSON serialization for Redis/Celery."""
        return self.model_dump_json()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generation": 10,
                "candidates": [
                    {
                        "id": "candidate-1",
                        "genome_data": {"assignments": []},
                        "fitness": 0.9,
                        "generation": 10,
                    }
                ],
            }
        }
    )
