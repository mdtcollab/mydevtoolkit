"""Catalog manifest for tracking installed items per project."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class CatalogManifest:
    """Tracks which catalog items are installed in a project."""

    def __init__(self, items: dict[str, dict[str, Any]] | None = None) -> None:
        self._items: dict[str, dict[str, Any]] = items or {}

    @staticmethod
    def _normalize_record(name: str, record: dict[str, Any]) -> dict[str, Any]:
        install_target = record.get("install_target") or record.get("target") or ""
        logical_consumers = list(record.get("logical_consumers") or [])
        if not logical_consumers:
            fallback_consumer = record.get("target") or install_target
            logical_consumers = [fallback_consumer] if fallback_consumer else []

        target = record.get("target") or (logical_consumers[0] if logical_consumers else install_target)
        source_hash = record.get("source_hash", "")
        installed_hash = record.get("installed_hash") or source_hash
        central_last_edited_at = record.get("central_last_edited_at")
        project_last_edited_at = record.get("project_last_edited_at") or central_last_edited_at

        normalized = dict(record)
        normalized.setdefault("name", name)
        normalized["install_target"] = install_target
        normalized["logical_consumers"] = logical_consumers
        normalized["target"] = target
        normalized["source_hash"] = source_hash
        normalized["installed_hash"] = installed_hash
        normalized.setdefault("installed_path", "")
        normalized.setdefault("installed_paths", [normalized["installed_path"]] if normalized["installed_path"] else [])
        normalized["central_last_edited_at"] = central_last_edited_at
        normalized["project_last_edited_at"] = project_last_edited_at
        return normalized

    @classmethod
    def load(cls, project_root: Path) -> CatalogManifest:
        """Load manifest from .mdt/catalog.json, or return empty manifest."""
        manifest_path = project_root / ".mdt" / "catalog.json"
        if not manifest_path.is_file():
            return cls()
        with open(manifest_path) as f:
            data = json.load(f)
        items = {
            name: cls._normalize_record(name, record)
            for name, record in data.get("items", {}).items()
        }
        return cls(items=items)

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
        target: str | None = None,
        install_target: str | None = None,
        logical_consumers: list[str] | None = None,
        install_mode: str,
        installed_path: str,
        source_hash: str,
        installed_hash: str | None = None,
        installed_paths: list[str] | None = None,
        central_last_edited_at: str | None = None,
        project_last_edited_at: str | None = None,
    ) -> None:
        """Record an installed item."""
        effective_install_target = install_target or target or ""
        effective_consumers = list(logical_consumers or ([target] if target else []))
        if not effective_consumers and effective_install_target:
            effective_consumers = [effective_install_target]

        self._items[name] = self._normalize_record(name, {
            "kind": kind,
            "target": target or (effective_consumers[0] if effective_consumers else effective_install_target),
            "install_target": effective_install_target,
            "logical_consumers": effective_consumers,
            "install_mode": install_mode,
            "installed_path": installed_path,
            "installed_paths": installed_paths or ([installed_path] if installed_path else []),
            "source_hash": source_hash,
            "installed_hash": installed_hash or source_hash,
            "central_last_edited_at": central_last_edited_at,
            "project_last_edited_at": project_last_edited_at or central_last_edited_at,
            "installed_at": datetime.now(timezone.utc).isoformat(),
        })

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

    def classify_state(
        self,
        name: str,
        *,
        central_hash: str,
        project_hash: str | None,
        exists_in_project: bool,
        is_symlink: bool = False,
        central_last_edited_at: str | None = None,
        project_last_edited_at: str | None = None,
    ) -> str | None:
        """Classify the current managed-skill state for a recorded item."""
        record = self._items.get(name)
        if record is None:
            return None
        if not exists_in_project:
            return "missing"
        if is_symlink:
            return "symlinked"

        baseline_hash = record.get("installed_hash") or record.get("source_hash") or ""
        if project_hash == central_hash:
            return "in sync"
        if central_hash != baseline_hash and project_hash == baseline_hash:
            return "central newer"
        if project_hash != baseline_hash and central_hash == baseline_hash:
            return "project newer"

        central_ts = _parse_timestamp(central_last_edited_at or record.get("central_last_edited_at"))
        project_ts = _parse_timestamp(project_last_edited_at or record.get("project_last_edited_at"))
        if central_ts and project_ts:
            return "project newer" if project_ts > central_ts else "central newer"

        if project_hash == baseline_hash:
            return "central newer"
        return "project newer"

    def list_installed(self) -> list[dict[str, Any]]:
        """Return all installed item records with names."""
        return [{"name": name, **record} for name, record in self._items.items()]

