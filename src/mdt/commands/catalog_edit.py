"""catalog_edit command: open a catalog item in an external editor."""

from __future__ import annotations

from mdt.catalog.editor import CatalogEditor
from mdt.catalog.manifest import CatalogManifest
from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogEditCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        if not args:
            return CommandResult(success=False, error="Usage: catalog edit <name>")

        name = args[0]
        catalog = CatalogRegistry()
        item = catalog.get_item(name)
        project_root = context.repo_root or context.cwd
        manifest = CatalogManifest.load(project_root)
        record = manifest.get(name)
        source_exists = (catalog.root / name / "source").exists()
        if item is None and not (record and source_exists):
            return CommandResult(success=False, error=f"Catalog item '{name}' not found.")

        editor_helper = CatalogEditor(catalog.root)
        try:
            editor_cmd = editor_helper.resolve_editor()
        except RuntimeError as e:
            return CommandResult(success=False, error=str(e))

        source_path = editor_helper.resolve_source_path(item or name)
        cmd = editor_cmd.split() + [str(source_path)]

        return CommandResult(
            success=True,
            output=f"Opening '{name}' in {editor_cmd}...",
            data={"run_external": cmd},
        )

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        if position == 0:
            from mdt.catalog.registry import CatalogRegistry
            from mdt.catalog.manifest import CatalogManifest
            from mdt.core.context import ProjectContext
            prefix = tokens[0].lower() if tokens else ""
            catalog = CatalogRegistry()
            names = {item.name for item in catalog.list_items() if item.name.startswith(prefix)}
            try:
                ctx = ProjectContext.detect()
                project_root = ctx.repo_root or ctx.cwd
                names.update(
                    record["name"] for record in CatalogManifest.load(project_root).list_installed()
                    if record["name"].startswith(prefix)
                )
            except Exception:  # noqa: BLE001
                pass
            return sorted(names)
        return []
