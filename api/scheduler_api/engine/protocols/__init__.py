"""Structural interfaces for the GA engine."""

from scheduler_api.engine.protocols.component import Component
from scheduler_api.engine.protocols.controller import SolverController
from scheduler_api.engine.protocols.culler import Culler
from scheduler_api.engine.protocols.executor import SolverExecutor
from scheduler_api.engine.protocols.mutator import Mutator
from scheduler_api.engine.protocols.runner import Runner
from scheduler_api.engine.protocols.scorer import Scorer
from scheduler_api.engine.protocols.seeder import Seeder
from scheduler_api.engine.protocols.selector import Selector
from scheduler_api.engine.protocols.solver import Solver
from scheduler_api.engine.protocols.stopper import Stopper

__all__ = [
    "Component",
    "Culler",
    "Mutator",
    "Runner",
    "Scorer",
    "Seeder",
    "Selector",
    "Solver",
    "SolverController",
    "SolverExecutor",
    "Stopper",
]
