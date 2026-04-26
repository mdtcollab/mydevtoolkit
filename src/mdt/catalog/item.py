"""Catalog item data model with YAML loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class TargetConfig:
    """Per-target install configuration."""

    install_mode: str  # "symlink", "copy", or "render"
    path_template: str  # e.g. ".claude/skills/{name}/SKILL.md"
    consumers: list[str] = field(default_factory=list)

    def resolve_path(self, name: str) -> str:
        """Resolve the path template with the given item name."""
        return self.path_template.format(name=name)


@dataclass(slots=True)
class CatalogItem:
    """A catalog item with metadata, classification tags, and target configs."""

    name: str
    kind: str  # "instruction", "prompt", "skill", or "agent"
    description: str = ""
    tags: dict[str, list[str]] = field(default_factory=dict)
    targets: dict[str, TargetConfig] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=dict)

    @property
    def source_files(self) -> list[str]:
        """Return the list of source file relative paths."""
        return self.source.get("files", [])

    @classmethod
    def from_yaml(cls, path: Path) -> CatalogItem:
        """Load a CatalogItem from a catalog-item.yaml file.

        Raises FileNotFoundError if the path does not exist.
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        targets = {}
        for target_name, target_data in (data.get("targets") or {}).items():
            targets[target_name] = TargetConfig(
                install_mode=target_data["install_mode"],
                path_template=target_data["path_template"],
                consumers=list(target_data.get("consumers") or [target_name]),
            )

        return cls(
            name=data["name"],
            kind=data["kind"],
            description=data.get("description", ""),
            tags=data.get("tags") or {},
            targets=targets,
            source=data.get("source") or {},
        )

