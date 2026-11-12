"""Genetic algorithm scheduling engine.

The engine is deliberately free of persistence, web framework, and broker
dependencies. See ``DESIGN.md`` (repository root) for the design specification.
"""

from scheduler_api.engine.controller import GAController
from scheduler_api.engine.execution.local import LocalExecutor
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.execution.store import InMemoryExecutionStore
from scheduler_api.engine.solver import GeneticAlgorithmSolver, default_solver_settings

__all__ = [
    "ComponentRegistry",
    "ComponentRunner",
    "GAController",
    "GeneticAlgorithmSolver",
    "InMemoryExecutionStore",
    "LocalExecutor",
    "default_solver_settings",
]
