"""TYPE_CHECKING-only protocol conformance checks.

CI has no type checker. Run Pyright or mypy locally to validate these
assignments; this module has no runtime effect.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scheduler_api.engine.protocols import (
        Culler,
        Mutator,
        Scorer,
        Seeder,
        Selector,
        Stopper,
    )

    _component_protocols: tuple[object, ...] = (
        Seeder,
        Scorer,
        Selector,
        Mutator,
        Culler,
        Stopper,
    )
