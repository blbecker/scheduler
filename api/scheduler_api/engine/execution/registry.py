from __future__ import annotations

from typing import cast

from scheduler_api.engine.exceptions import (
    ComponentCategoryMismatchError,
    ComponentNotFoundError,
    DuplicateComponentError,
    EngineValidationError,
)
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.protocols import (
    Component,
    Culler,
    Mutator,
    Scorer,
    Seeder,
    Selector,
    Stopper,
)


class ComponentRegistry:
    """Explicit per-category component ID to implementation map."""

    def __init__(self) -> None:
        self._components: dict[ComponentCategory, dict[str, Component]] = {
            category: {} for category in ComponentCategory
        }

    def register(
        self,
        category: ComponentCategory,
        component_id: str,
        component: Component,
    ) -> None:
        if not component_id:
            raise EngineValidationError("component ID must be non-empty")
        if component.component_category != category:
            raise ComponentCategoryMismatchError(
                f"component {component_id} declares category "
                f"{component.component_category.value}, "
                f"registered as {category.value}",
                component_id=component_id,
            )
        components = self._components[category]
        if component_id in components:
            raise DuplicateComponentError(component_id, category)
        components[component_id] = component

    def resolve(
        self,
        category: ComponentCategory,
        component_id: str,
    ) -> Component:
        try:
            return self._components[category][component_id]
        except KeyError as exc:
            raise ComponentNotFoundError(component_id, category) from exc

    def register_seeder(self, component_id: str, component: Seeder) -> None:
        self.register(ComponentCategory.SEEDER, component_id, component)

    def resolve_seeder(self, component_id: str) -> Seeder:
        return cast(Seeder, self.resolve(ComponentCategory.SEEDER, component_id))

    def register_scorer(self, component_id: str, component: Scorer) -> None:
        self.register(ComponentCategory.SCORER, component_id, component)

    def resolve_scorer(self, component_id: str) -> Scorer:
        return cast(Scorer, self.resolve(ComponentCategory.SCORER, component_id))

    def register_selector(self, component_id: str, component: Selector) -> None:
        self.register(ComponentCategory.SELECTOR, component_id, component)

    def resolve_selector(self, component_id: str) -> Selector:
        return cast(Selector, self.resolve(ComponentCategory.SELECTOR, component_id))

    def register_mutator(self, component_id: str, component: Mutator) -> None:
        self.register(ComponentCategory.MUTATOR, component_id, component)

    def resolve_mutator(self, component_id: str) -> Mutator:
        return cast(Mutator, self.resolve(ComponentCategory.MUTATOR, component_id))

    def register_culler(self, component_id: str, component: Culler) -> None:
        self.register(ComponentCategory.CULLER, component_id, component)

    def resolve_culler(self, component_id: str) -> Culler:
        return cast(Culler, self.resolve(ComponentCategory.CULLER, component_id))

    def register_stopper(self, component_id: str, component: Stopper) -> None:
        self.register(ComponentCategory.STOPPER, component_id, component)

    def resolve_stopper(self, component_id: str) -> Stopper:
        return cast(Stopper, self.resolve(ComponentCategory.STOPPER, component_id))
