"""TYPE_CHECKING-only protocol conformance checks.

CI has no type checker. Run Pyright or mypy locally to validate these
assignments; this module has no runtime effect.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scheduler_api.engine.components import (
        CoverageScorer,
        GenerationCountStopper,
        RandomReplacementMutator,
        RandomScheduleSeeder,
        ShiftLengthScorer,
        SkillsMatchScorer,
        TopNCuller,
        TopNSelector,
        WorkerOverlapScorer,
    )
    from scheduler_api.engine.protocols import (
        Culler,
        Mutator,
        Scorer,
        Seeder,
        Selector,
        Stopper,
    )

    _seeder: Seeder = RandomScheduleSeeder()
    _skills: Scorer = SkillsMatchScorer()
    _overlap: Scorer = WorkerOverlapScorer()
    _coverage: Scorer = CoverageScorer()
    _shift_length: Scorer = ShiftLengthScorer()
    _selector: Selector = TopNSelector()
    _mutator: Mutator = RandomReplacementMutator()
    _culler: Culler = TopNCuller()
    _stopper: Stopper = GenerationCountStopper()
