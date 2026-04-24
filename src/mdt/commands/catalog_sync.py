"""catalog_sync command: re-sync installed items, detecting drift."""

from __future__ import annotations

import hashlib
from pathlib import Path

from mdt.catalog.installer import CatalogInstaller
from mdt.catalog.manifest import CatalogManifest
from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


def _hash_files(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


class CatalogSyncCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args
        project_root = context.repo_root or context.cwd
        manifest = CatalogManifest.load(project_root)
        catalog = CatalogRegistry()
        installer = CatalogInstaller(catalog.root)

        installed = manifest.list_installed()
        if not installed:
            return CommandResult(success=True, output="No catalog items installed.")

        updated = []
        for record in installed:
            name = record["name"]
            item = catalog.get_item(name)
            if item is None:
                continue

            source_dir = catalog.root / name / "source"
            source_files = [source_dir / f for f in item.source_files]
            current_hash = _hash_files(source_files)

            if manifest.check_drift(name, current_hash):
                target = record["target"]
                try:
                    installer.install(item, target=target, project_root=project_root, manifest=manifest)
                    updated.append(name)
                except ValueError:
                    pass

        manifest.save(project_root)

        if not updated:
            return CommandResult(success=True, output="All installed items are up to date.")

        lines = ["Synced items:"] + [f"  - {name}" for name in updated]
        return CommandResult(success=True, output="\n".join(lines))

