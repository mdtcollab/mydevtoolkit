"""catalog_sync command: re-sync installed items, detecting managed-skill freshness."""

from __future__ import annotations

from mdt.catalog.installer import CatalogInstaller
from mdt.catalog.manifest import CatalogManifest
from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult
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

        status_by_name = {status.name: status for status in catalog.get_managed_skill_statuses(project_root)}
        updated: list[str] = []
        noted: list[str] = []
        for record in installed:
            name = record["name"]
            status = status_by_name.get(name)
            if status is None:
                continue
            item = catalog.get_item(name)
            if item is None and status.state == "central newer":
                continue

            if status.state == "central newer" and item is not None:
                target = record.get("install_target") or record.get("target")
                try:
                    installer.install(item, target=target, project_root=project_root, manifest=manifest)
                    updated.append(name)
                except ValueError:
                    noted.append(f"  - {name}: unable to resolve install target")
            elif status.state in {"project newer", "symlinked", "missing", "project only"}:
                noted.append(f"  - {name}: {status.state}")

        manifest.save(project_root)

        if not updated and not noted:
            return CommandResult(success=True, output="All installed items are up to date.")

        lines: list[str] = []
        if updated:
            lines.extend(["Synced items:", *[f"  - {name}" for name in updated]])
        if noted:
            if lines:
                lines.append("")
            lines.extend(["Status:", *noted])
        return CommandResult(success=True, output="\n".join(lines))

