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
SHARED_HELPER_MODULES = {
    "scheduler_api.engine.exceptions",
    "scheduler_api.engine.ranking",
    "scheduler_api.engine.randomness",
    "scheduler_api.engine.validation",
}
LAYER_ALLOWED_ENGINE_IMPORTS = {
    "models/": ("scheduler_api.engine.models",),
    "protocols/": (
        "scheduler_api.engine.models",
        "scheduler_api.engine.protocols",
        "scheduler_api.engine.execution.registry",
    ),
    "components/": (
        "scheduler_api.engine.components",
        "scheduler_api.engine.models",
        "scheduler_api.engine.protocols",
        *SHARED_HELPER_MODULES,
    ),
    "aggregation.py": (
        "scheduler_api.engine.models",
        *SHARED_HELPER_MODULES,
    ),
    "execution/": (
        "scheduler_api.engine.execution",
        "scheduler_api.engine.models",
        "scheduler_api.engine.protocols",
        *SHARED_HELPER_MODULES,
    ),
}
FORBIDDEN_INTERNAL_IMPORTS = {
    "controller.py": {"scheduler_api.engine.solver"},
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
            modules.update(f"{node.module}.{alias.name}" for alias in node.names)
    return modules


def engine_imports(tree: ast.AST) -> set[str]:
    return {
        module
        for module in imported_modules(tree)
        if module == "scheduler_api.engine"
        or module.startswith("scheduler_api.engine.")
    }


def matches_prefix(module: str, prefix: str) -> bool:
    return module == prefix or module.startswith(prefix + ".")


def test_import_scan_catches_from_scheduler_api_import_db():
    modules = imported_modules(ast.parse("from scheduler_api import db"))

    assert "scheduler_api.db" in modules


def test_engine_has_no_forbidden_imports():
    violations: list[str] = []
    for path in engine_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for module in imported_modules(tree):
            for forbidden in FORBIDDEN_MODULES:
                if module == forbidden or module.startswith(forbidden + "."):
                    violations.append(f"{path}: {module}")
    assert not violations


def test_engine_internal_layers_respect_dependency_rules():
    violations: list[str] = []
    for path in engine_files():
        relative = path.relative_to(ENGINE_DIR).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = engine_imports(tree)

        for layer, allowed in LAYER_ALLOWED_ENGINE_IMPORTS.items():
            is_member = (
                relative.startswith(layer)
                if layer.endswith("/")
                else (relative == layer)
            )
            if not is_member:
                continue
            for module in modules:
                if not any(matches_prefix(module, prefix) for prefix in allowed):
                    violations.append(f"{relative}: {module}")

        for name, forbidden in FORBIDDEN_INTERNAL_IMPORTS.items():
            if relative != name:
                continue
            for module in modules:
                if any(matches_prefix(module, prefix) for prefix in forbidden):
                    violations.append(f"{relative}: {module}")

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
