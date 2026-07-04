"""Schedule solve pipeline configuration."""

from typing import Dict, List, Any
from ..interfaces import (
    GenomeOperator,
    Scorable,
    Constraint,
    Selector,
    Seeder,
    Stoppable,
)
from .genome import ScheduleGenome
from .context import ScheduleSolveContext


class ScheduleSolvePipeline:
    """Container for schedule solve pipeline components."""

    def __init__(
        self,
        seeders: List[Seeder[ScheduleGenome, ScheduleSolveContext]],
        genome_operators: List[GenomeOperator[ScheduleGenome, ScheduleSolveContext]],
        scorers: List[Scorable[ScheduleGenome, ScheduleSolveContext]],
        constraints: List[Constraint[ScheduleGenome, ScheduleSolveContext]],
        selector: Selector[ScheduleGenome, ScheduleSolveContext],
        stop_conditions: List[Stoppable[List[ScheduleGenome], ScheduleSolveContext]],
    ):
        self.seeders = seeders
        self.genome_operators = genome_operators
        self.scorers = scorers
        self.constraints = constraints
        self.selector = selector
        self.stop_conditions = stop_conditions

    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary representation."""
        return {
            "seeders": self.seeders,
            "genome_operators": self.genome_operators,
            "scorers": self.scorers,
            "constraints": self.constraints,
            "selector": self.selector,
            "stop_conditions": self.stop_conditions,
        }
