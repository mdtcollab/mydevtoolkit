"""catalog_edit command: open a catalog item in an external editor."""

from __future__ import annotations

from mdt.catalog.editor import CatalogEditor
from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogEditCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del context
        if not args:
            return CommandResult(success=False, error="Usage: catalog edit <name>")

        name = args[0]
        catalog = CatalogRegistry()
        item = catalog.get_item(name)
        if item is None:
            return CommandResult(success=False, error=f"Catalog item '{name}' not found.")

        editor_helper = CatalogEditor(catalog.root)
        try:
            editor_cmd = editor_helper.resolve_editor()
        except RuntimeError as e:
            return CommandResult(success=False, error=str(e))

        source_path = editor_helper.resolve_source_path(item)
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
            prefix = tokens[0].lower() if tokens else ""
            catalog = CatalogRegistry()
            return sorted(
                item.name for item in catalog.list_items()
                if item.name.startswith(prefix)
            )
        return []
