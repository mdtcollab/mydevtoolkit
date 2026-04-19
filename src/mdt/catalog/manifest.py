"""Catalog manifest for tracking installed items per project."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CatalogManifest:
    """Tracks which catalog items are installed in a project."""

    def __init__(self, items: dict[str, dict[str, Any]] | None = None) -> None:
        self._items: dict[str, dict[str, Any]] = items or {}

    @classmethod
    def load(cls, project_root: Path) -> CatalogManifest:
        """Load manifest from .mdt/catalog.json, or return empty manifest."""
        manifest_path = project_root / ".mdt" / "catalog.json"
        if not manifest_path.is_file():
            return cls()
        with open(manifest_path) as f:
            data = json.load(f)
        return cls(items=data.get("items", {}))

    def save(self, project_root: Path) -> None:
        """Save manifest to .mdt/catalog.json, creating directory if needed."""
        mdt_dir = project_root / ".mdt"
        mdt_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = mdt_dir / "catalog.json"
        with open(manifest_path, "w") as f:
            json.dump({"items": self._items}, f, indent=2)

    def record_install(
        self,
        *,
        name: str,
        kind: str,
        target: str,
        install_mode: str,
        installed_path: str,
        source_hash: str,
    ) -> None:
        """Record an installed item."""
        self._items[name] = {
            "kind": kind,
            "target": target,
            "install_mode": install_mode,
            "installed_path": installed_path,
            "source_hash": source_hash,
            "installed_at": datetime.now(timezone.utc).isoformat(),
        }

    def get(self, name: str) -> dict[str, Any] | None:
        """Get a record by item name."""
        return self._items.get(name)

    def remove(self, name: str) -> None:
        """Remove a record by item name. No error if not found."""
        self._items.pop(name, None)

    def check_drift(self, name: str, current_hash: str) -> bool:
        """Return True if the source has changed since install."""
        record = self._items.get(name)
        if record is None:
            return False
        return record["source_hash"] != current_hash

    def list_installed(self) -> list[dict[str, Any]]:
        """Return all installed item records with names."""
        return [{"name": name, **record} for name, record in self._items.items()]

