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
            return CommandResult(success=False, error="Usage: catalog install <name> [<name> ...] --target <target>")

        names: list[str] = []
        target = None
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--target" and i + 1 < len(args):
                target = args[i + 1]
                break
            if not arg.startswith("--"):
                names.append(arg)
            i += 1

        if not names:
            return CommandResult(success=False, error="Usage: catalog install <name> [<name> ...] --target <target>")
        if not target:
            return CommandResult(success=False, error="Missing --target. Specify a target such as claude, copilot, shared_claude, or opencode.")

        catalog = CatalogRegistry()
        project_root = context.repo_root or context.cwd
        manifest = CatalogManifest.load(project_root)
        installer = CatalogInstaller(catalog.root)

        installed: list[str] = []
        for name in names:
            item = catalog.get_item(name)
            if item is None:
                return CommandResult(success=False, error=f"Catalog item '{name}' not found.")
            try:
                mode = installer.install(item, target=target, project_root=project_root, manifest=manifest)
            except ValueError as e:
                return CommandResult(success=False, error=str(e))
            installed.append(f"  - {name} ({mode})")

        manifest.save(project_root)
        if len(installed) == 1:
            return CommandResult(success=True, output=f"Installed '{names[0]}' for {target} ({installed[0].split('(')[-1].rstrip(')')})")
        return CommandResult(success=True, output="Installed items:\n" + "\n".join(installed))

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
            targets = ["claude", "copilot", "opencode", "shared_claude"]
            if tokens:
                catalog = CatalogRegistry()
                item = catalog.get_item(tokens[0])
                if item is not None:
                    dynamic_targets = set(item.targets)
                    for config in item.targets.values():
                        dynamic_targets.update(config.consumers)
                    targets = sorted(dynamic_targets)
            return [t for t in targets if t.startswith(prefix)]
        return []
