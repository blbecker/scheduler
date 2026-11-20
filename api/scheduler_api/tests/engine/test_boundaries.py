from __future__ import annotations

import ast
from pathlib import Path
from uuid import UUID

from scheduler_api.engine.execution.runner import TypedComponentRunner
from scheduler_api.engine.models.phase import PhaseResult
from scheduler_api.engine.solver import build_mvp_solver

from .factories import make_problem

ENGINE_DIR = Path(__file__).resolve().parents[2] / "engine"
FORBIDDEN_MODULES = {
    "celery",
    "fastapi",
    "sqlmodel",
    "sqlalchemy",
    "scheduler_api.db",
}


def engine_files() -> list[Path]:
    return sorted(ENGINE_DIR.rglob("*.py"))


def imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_engine_has_no_forbidden_imports():
    violations: list[str] = []
    for path in engine_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for module in imported_modules(tree):
            for forbidden in FORBIDDEN_MODULES:
                if module == forbidden or module.startswith(forbidden + "."):
                    violations.append(f"{path}: {module}")
    assert not violations


def test_model_and_phase_contracts_do_not_use_any():
    violations: list[str] = []
    for path in engine_files():
        if path.name == "_typecheck.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "Any":
                violations.append(str(path))
            elif isinstance(node, ast.Attribute) and node.attr == "Any":
                violations.append(str(path))
    assert not violations


def test_engine_package_init_has_no_heavy_imports():
    tree = ast.parse((ENGINE_DIR / "__init__.py").read_text(encoding="utf-8"))

    assert not [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]


def test_phase_plan_and_result_round_trip_through_json():
    solver = build_mvp_solver(population_size=2, max_generations=1)
    controller = solver.create_controller(make_problem())
    runner = TypedComponentRunner(solver.build_registry())
    plan = controller.start(UUID(int=1))
    assert plan is not None
    result = PhaseResult(
        execution_id=plan.execution_id,
        phase_execution_id=plan.phase_execution_id,
        results=tuple(runner.run(invocation) for invocation in plan.invocations),
    )

    for payload in (plan, result):
        restored = type(payload).model_validate(payload.model_dump(mode="json"))
        assert restored == payload
