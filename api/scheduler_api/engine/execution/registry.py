"""Explicit component registration and resolution."""

from __future__ import annotations

from typing import Any, cast

from scheduler_api.engine.errors import ComponentCategoryError, UnknownComponentError
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.protocols.component import AnyComponent
from scheduler_api.engine.protocols.culler import Culler
from scheduler_api.engine.protocols.mutator import Mutator
from scheduler_api.engine.protocols.scorer import Scorer
from scheduler_api.engine.protocols.seeder import Seeder
from scheduler_api.engine.protocols.selector import Selector
from scheduler_api.engine.protocols.stopper import Stopper
from scheduler_api.engine.models.component_io import (
    CullResult,
    GenerationCountStopInput,
    MutateResult,
    RandomShiftMutateInput,
    ScoreInput,
    ScoreResult,
    SeedRandomShiftsInput,
    SeedResult,
    SelectResult,
    StopResult,
    TopNCullInput,
    TopNSelectInput,
)


class ComponentRegistry:
    """Maps stable component ids to implementations.

    Component ids are unique across *all* categories, not per category: the
    invocation input union discriminates on ``component_id`` alone, so a
    duplicate anywhere would make a plan ambiguous.
    """

    def __init__(self) -> None:
        self._components: dict[str, AnyComponent] = {}
        self._categories: dict[str, ComponentCategory] = {}

    def _register(
        self, component_id: str, category: ComponentCategory, component: AnyComponent
    ) -> None:
        declared = getattr(component, "component_id", None)
        if declared != component_id:
            raise ComponentCategoryError(
                f"component registered as {component_id!r} declares component_id {declared!r}"
            )
        if component_id in self._components:
            raise ComponentCategoryError(
                f"component id {component_id!r} is already registered as "
                f"{self._categories[component_id].value}"
            )
        self._components[component_id] = component
        self._categories[component_id] = category

    def register_seeder(self, component_id: str, component: Seeder[Any, Any]) -> None:
        self._register(component_id, ComponentCategory.SEEDER, component)

    def register_scorer(self, component_id: str, component: Scorer[Any, Any]) -> None:
        self._register(component_id, ComponentCategory.SCORER, component)

    def register_selector(
        self, component_id: str, component: Selector[Any, Any]
    ) -> None:
        self._register(component_id, ComponentCategory.SELECTOR, component)

    def register_mutator(
        self,
        component_id: str,
        component: Mutator[Any, Any],
    ) -> None:
        self._register(component_id, ComponentCategory.MUTATOR, component)

    def register_culler(self, component_id: str, component: Culler[Any, Any]) -> None:
        self._register(component_id, ComponentCategory.CULLER, component)

    def register_stopper(
        self,
        component_id: str,
        component: Stopper[Any, Any],
    ) -> None:
        self._register(component_id, ComponentCategory.STOPPER, component)

    def resolve(self, category: ComponentCategory, component_id: str) -> AnyComponent:
        """Return the implementation registered for an id, checking the category."""
        component = self._components.get(component_id)
        if component is None:
            raise UnknownComponentError(
                f"no component registered with id {component_id!r}"
            )
        registered_category = self._categories[component_id]
        if registered_category is not category:
            raise ComponentCategoryError(
                f"component {component_id!r} is registered as {registered_category.value}, "
                f"not {category.value}"
            )
        return component

    def category_of(self, component_id: str) -> ComponentCategory:
        try:
            return self._categories[component_id]
        except KeyError as exc:
            raise UnknownComponentError(
                f"no component registered with id {component_id!r}"
            ) from exc

    def component_ids(self) -> frozenset[str]:
        return frozenset(self._components)

    def components_in(self, category: ComponentCategory) -> frozenset[str]:
        return frozenset(
            component_id
            for component_id, registered in self._categories.items()
            if registered is category
        )


def as_seeder(component: AnyComponent) -> Seeder[SeedRandomShiftsInput, SeedResult]:
    return cast(Seeder[SeedRandomShiftsInput, SeedResult], component)


def as_scorer(component: AnyComponent) -> Scorer[ScoreInput, ScoreResult]:
    return cast(Scorer[ScoreInput, ScoreResult], component)


def as_selector(component: AnyComponent) -> Selector[TopNSelectInput, SelectResult]:
    return cast(Selector[TopNSelectInput, SelectResult], component)


def as_mutator(
    component: AnyComponent,
) -> Mutator[RandomShiftMutateInput, MutateResult]:
    return cast(Mutator[RandomShiftMutateInput, MutateResult], component)


def as_culler(component: AnyComponent) -> Culler[TopNCullInput, CullResult]:
    return cast(Culler[TopNCullInput, CullResult], component)


def as_stopper(
    component: AnyComponent,
) -> Stopper[GenerationCountStopInput, StopResult]:
    return cast(Stopper[GenerationCountStopInput, StopResult], component)
