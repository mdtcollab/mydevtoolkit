"""catalog_install command: install a catalog item into the project."""

from __future__ import annotations

from mdt.catalog.installer import CatalogInstaller
from mdt.catalog.manifest import CatalogManifest
from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogInstallCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        if not args:
            return CommandResult(success=False, error="Usage: catalog install <name> --target <target>")

        name = args[0]
        target = None
        for i, arg in enumerate(args):
            if arg == "--target" and i + 1 < len(args):
                target = args[i + 1]
                break

        if not target:
            return CommandResult(success=False, error="Missing --target. Specify claude, copilot, or opencode.")

        catalog = CatalogRegistry()
        item = catalog.get_item(name)
        if item is None:
            return CommandResult(success=False, error=f"Catalog item '{name}' not found.")

        project_root = context.repo_root or context.cwd
        manifest = CatalogManifest.load(project_root)
        installer = CatalogInstaller(catalog.root)

        try:
            mode = installer.install(item, target=target, project_root=project_root, manifest=manifest)
        except ValueError as e:
            return CommandResult(success=False, error=str(e))

        manifest.save(project_root)
        return CommandResult(
            success=True,
            output=f"Installed '{name}' for {target} (mode: {mode})",
        )

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        if position == 0:
            from mdt.catalog.registry import CatalogRegistry
            prefix = tokens[0].lower() if tokens else ""
            catalog = CatalogRegistry()
            return sorted(
                item.name for item in catalog.list_items()
                if item.name.startswith(prefix)
            )
        if position == 1:
            prefix = tokens[1].lower() if len(tokens) > 1 else ""
            return [f for f in ["--target"] if f.startswith(prefix)]
        if position == 2:
            prefix = tokens[2].lower() if len(tokens) > 2 else ""
            targets = ["claude", "copilot", "opencode"]
            return [t for t in targets if t.startswith(prefix)]
        return []
