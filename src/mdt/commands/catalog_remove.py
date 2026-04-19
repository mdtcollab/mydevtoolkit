"""catalog_remove command: remove an installed catalog item from the project."""

from __future__ import annotations

from pathlib import Path

from mdt.catalog.manifest import CatalogManifest
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogRemoveCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        if not args:
            return CommandResult(success=False, error="Usage: catalog remove <name>")

        name = args[0]
        project_root = context.repo_root or context.cwd
        manifest = CatalogManifest.load(project_root)

        record = manifest.get(name)
        if record is None:
            return CommandResult(success=False, error=f"Item '{name}' is not installed in this project.")

        # Remove the installed file(s)
        installed_path = project_root / record["installed_path"]
        if installed_path.is_symlink() or installed_path.is_file():
            installed_path.unlink()
        elif installed_path.is_dir():
            import shutil
            shutil.rmtree(installed_path)

        # Clean up empty parent directories
        parent = installed_path.parent
        while parent != project_root and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent

        manifest.remove(name)
        manifest.save(project_root)
        return CommandResult(success=True, output=f"Removed '{name}' from project.")

