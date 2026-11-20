from __future__ import annotations

import pytest

from scheduler_api.engine.exceptions import (
    ComponentCategoryMismatchError,
    ComponentNotFoundError,
    DuplicateComponentError,
)
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.models.phase import ComponentCategory


class FakeComponent:
    def __init__(self, category: ComponentCategory) -> None:
        self.component_category = category


@pytest.mark.parametrize("category", list(ComponentCategory))
def test_register_and_resolve_every_category(category):
    registry = ComponentRegistry()
    component = FakeComponent(category)

    registry.register(category, "component", component)

    assert registry.resolve(category, "component") is component


def test_typed_wrappers_register_and_resolve_by_category():
    registry = ComponentRegistry()
    component = FakeComponent(ComponentCategory.SEEDER)

    registry.register_seeder("seed", component)

    assert registry.resolve_seeder("seed") is component


def test_duplicate_id_in_same_category_is_rejected():
    registry = ComponentRegistry()
    component = FakeComponent(ComponentCategory.SCORER)
    registry.register(ComponentCategory.SCORER, "score", component)

    with pytest.raises(DuplicateComponentError):
        registry.register(ComponentCategory.SCORER, "score", component)


def test_same_id_in_different_categories_is_allowed():
    registry = ComponentRegistry()
    selector = FakeComponent(ComponentCategory.SELECTOR)
    culler = FakeComponent(ComponentCategory.CULLER)

    registry.register(ComponentCategory.SELECTOR, "top_n", selector)
    registry.register(ComponentCategory.CULLER, "top_n", culler)

    assert registry.resolve_selector("top_n") is selector
    assert registry.resolve_culler("top_n") is culler


def test_unknown_id_is_rejected():
    registry = ComponentRegistry()

    with pytest.raises(ComponentNotFoundError):
        registry.resolve(ComponentCategory.SEEDER, "missing")


def test_category_mismatch_is_rejected():
    registry = ComponentRegistry()
    component = FakeComponent(ComponentCategory.SCORER)

    with pytest.raises(ComponentCategoryMismatchError):
        registry.register(ComponentCategory.SEEDER, "wrong", component)
