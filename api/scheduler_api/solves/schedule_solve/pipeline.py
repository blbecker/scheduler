"""Schedule solve pipeline configuration."""

from typing import Any
from scheduler_api.engine.interfaces import (
    GenomeOperator,
    Scorable,
    Constraint,
    Selector,
    Seeder,
    Stoppable,
)
from scheduler_api.domain.schedule import Schedule
from .context import ScheduleSolveContext


class ScheduleSolvePipeline:
    """Container for schedule solve pipeline components."""

    def __init__(
        self,
        seeders: list[Seeder[Schedule, ScheduleSolveContext]],
        genome_operators: list[GenomeOperator[Schedule, ScheduleSolveContext]],
        scorers: list[Scorable[Schedule, ScheduleSolveContext]],
        constraints: list[Constraint[Schedule, ScheduleSolveContext]],
        selector: Selector[Schedule, ScheduleSolveContext],
        stop_conditions: list[Stoppable[list[Schedule], ScheduleSolveContext]],
    ):
        self.seeders = seeders
        self.genome_operators = genome_operators
        self.scorers = scorers
        self.constraints = constraints
        self.selector = selector
        self.stop_conditions = stop_conditions

    def to_dict(self) -> dict[str, Any]:
        """Convert pipeline to dictionary representation."""
        return {
            "seeders": self.seeders,
            "genome_operators": self.genome_operators,
            "scorers": self.scorers,
            "constraints": self.constraints,
            "selector": self.selector,
            "stop_conditions": self.stop_conditions,
        }
