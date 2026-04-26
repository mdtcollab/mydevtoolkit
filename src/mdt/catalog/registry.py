"""Catalog registry for discovering and filtering catalog items."""

from __future__ import annotations

import os
from pathlib import Path

from mdt.catalog.item import CatalogItem
from mdt.catalog.managed_skills import (
    build_managed_skill_statuses,
    discover_project_skills,
    item_supports_target,
)


DEFAULT_CATALOG_PATH = Path.home() / ".config" / "mdt" / "catalog"


def _get_catalog_root(override: Path | None = None) -> Path:
    """Return the catalog root path, checking override, env var, then default."""
    if override is not None:
        return override
    env = os.environ.get("MDT_CATALOG_PATH")
    if env:
        return Path(env)
    return DEFAULT_CATALOG_PATH


class CatalogRegistry:
    """Discovers and filters catalog items from the catalog root directory."""

    def __init__(self, catalog_root: Path | None = None) -> None:
        self._root = _get_catalog_root(catalog_root)

    @property
    def root(self) -> Path:
        return self._root

    def list_items(
        self,
        *,
        kind: str | None = None,
        tag: tuple[str, str] | None = None,
        target: str | None = None,
    ) -> list[CatalogItem]:
        """List all catalog items, optionally filtered."""
        if not self._root.is_dir():
            return []

        items: list[CatalogItem] = []
        for child in sorted(self._root.iterdir()):
            yaml_path = child / "catalog-item.yaml"
            if child.is_dir() and yaml_path.is_file():
                try:
                    item = CatalogItem.from_yaml(yaml_path)
                except Exception:  # noqa: BLE001
                    continue
                if kind and item.kind != kind:
                    continue
                if tag:
                    tag_key, tag_value = tag
                    if tag_value not in item.tags.get(tag_key, []):
                        continue
                if target and not item_supports_target(item, target):
                    continue
                items.append(item)
        return items

    def get_item(self, name: str) -> CatalogItem | None:
        """Get a single catalog item by name, or None if not found."""
        yaml_path = self._root / name / "catalog-item.yaml"
        if not yaml_path.is_file():
            return None
        try:
            return CatalogItem.from_yaml(yaml_path)
        except Exception:  # noqa: BLE001
            return None

    def discover_project_skills(self, project_root: Path) -> list:
        """Discover skill installations in known project locations."""
        return discover_project_skills(project_root)

    def get_managed_skill_statuses(self, project_root: Path) -> list:
        """Return correlated central/project managed-skill status entries."""
        return build_managed_skill_statuses(project_root, self._root)

