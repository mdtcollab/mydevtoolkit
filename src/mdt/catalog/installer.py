"""Catalog installer for installing items into projects."""

from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from mdt.catalog.item import CatalogItem
from mdt.catalog.manifest import CatalogManifest
from mdt.catalog.managed_skills import resolve_item_target
from mdt.catalog.renderer import CatalogRenderer


def _hash_file(path: Path) -> str:
    """Return SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_files(paths: list[Path]) -> str:
    """Return combined hash of multiple files."""
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.read_bytes())
    return h.hexdigest()


def _timestamp_for_path(path: Path) -> str | None:
    try:
        if path.is_symlink():
            stamp = path.lstat().st_mtime
        elif path.is_file():
            stamp = path.stat().st_mtime
        elif path.is_dir():
            stamp = max((child.stat().st_mtime for child in path.rglob("*") if child.is_file()), default=path.stat().st_mtime)
        else:
            return None
        return datetime.fromtimestamp(stamp, timezone.utc).isoformat()
    except OSError:
        return None


def _can_symlink(source: Path, target: Path) -> bool:
    """Check if symlink is feasible (same filesystem)."""
    try:
        source_dev = os.stat(source).st_dev
        # Target may not exist yet; check its parent
        target_parent = target.parent
        target_parent.mkdir(parents=True, exist_ok=True)
        target_dev = os.stat(target_parent).st_dev
        return source_dev == target_dev
    except OSError:
        return False


class CatalogInstaller:
    """Installs catalog items into projects using symlink, copy, or render."""

    def __init__(self, catalog_root: Path, renderer: CatalogRenderer | None = None) -> None:
        self._catalog_root = catalog_root
        self._renderer = renderer or CatalogRenderer()

    def install(
        self,
        item: CatalogItem,
        target: str,
        project_root: Path,
        manifest: CatalogManifest | None = None,
    ) -> str:
        """Install a catalog item into the project for the given target.

        Returns the install mode actually used (may differ from config if fallback).
        Raises ValueError if target is not supported by the item.
        """
        resolved_target = resolve_item_target(item, target)
        if resolved_target is None:
            raise ValueError(f"Item '{item.name}' does not support target '{target}'")

        target_name, target_config = resolved_target
        install_mode = target_config.install_mode
        source_dir = self._catalog_root / item.name / "source"
        source_files = [source_dir / f for f in item.source_files]

        if len(item.source_files) == 1:
            target_path = project_root / target_config.resolve_path(item.name)
            actual_mode = self._install_single(
                source_files[0], target_path, install_mode, target, item,
            )
            installed_path = target_config.resolve_path(item.name)
            installed_paths = [installed_path]
            installed_hash = _hash_files([target_path]) if target_path.exists() or target_path.is_symlink() else ""
            project_last_edited_at = _timestamp_for_path(target_path)
        else:
            # Multi-file: resolve path as directory
            base_path = project_root / target_config.resolve_path(item.name)
            target_dir = base_path.parent if "." in base_path.name else base_path
            actual_mode = self._install_multi(
                source_dir, item.source_files, target_dir, install_mode, target, item,
            )
            installed_path = str(target_dir.relative_to(project_root))
            installed_paths = [str((target_dir / f).relative_to(project_root)) for f in item.source_files]
            installed_hash = _hash_files([target_dir / f for f in item.source_files]) if installed_paths else ""
            project_last_edited_at = _timestamp_for_path(target_dir)

        # Update manifest if provided
        if manifest is not None:
            source_hash = _hash_files(source_files) if source_files else ""
            manifest.record_install(
                name=item.name,
                kind=item.kind,
                target=target,
                install_target=target_name,
                logical_consumers=list(target_config.consumers or [target_name]),
                install_mode=actual_mode,
                installed_path=installed_path,
                installed_paths=installed_paths,
                source_hash=source_hash,
                installed_hash=installed_hash,
                central_last_edited_at=_timestamp_for_path(source_dir),
                project_last_edited_at=project_last_edited_at,
            )

        return actual_mode

    def _install_single(
        self,
        source: Path,
        target_path: Path,
        mode: str,
        target_name: str,
        item: CatalogItem,
    ) -> str:
        """Install a single file. Returns actual mode used."""
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if mode == "symlink":
            if _can_symlink(source, target_path):
                try:
                    target_path.unlink(missing_ok=True)
                    target_path.symlink_to(source)
                    return "symlink"
                except OSError:
                    pass
            # Fallback to copy
            shutil.copy2(source, target_path)
            return "copy"

        if mode == "copy":
            shutil.copy2(source, target_path)
            return "copy"

        if mode == "render":
            content = source.read_text()
            rendered = self._renderer.render(content, source, target_name, item)
            target_path.write_text(rendered)
            return "render"

        raise ValueError(f"Unknown install mode: {mode}")

    def _install_multi(
        self,
        source_dir: Path,
        files: list[str],
        target_dir: Path,
        mode: str,
        target_name: str,
        item: CatalogItem,
    ) -> str:
        """Install multiple files. Returns actual mode used."""
        actual_mode = mode
        for filename in files:
            source = source_dir / filename
            target_path = target_dir / filename
            result_mode = self._install_single(source, target_path, mode, target_name, item)
            actual_mode = result_mode  # Use last mode (they should all be the same)
        return actual_mode

