"""Catalog renderer for target-specific content transformation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from mdt.catalog.item import CatalogItem

RenderFunc = Callable[[str, Path, CatalogItem], str]


class CatalogRenderer:
    """Transforms canonical source content into target-specific formats."""

    def __init__(self) -> None:
        self._renderers: dict[str, RenderFunc] = {}

    def register(self, target: str, func: RenderFunc) -> None:
        """Register a render function for a target."""
        self._renderers[target] = func

    def render(self, content: str, source_path: Path, target: str, item: CatalogItem | None = None) -> str:
        """Render content for a target. Falls back to passthrough if no renderer registered."""
        func = self._renderers.get(target)
        if func is None:
            return content
        return func(content, source_path, item)  # type: ignore[arg-type]

