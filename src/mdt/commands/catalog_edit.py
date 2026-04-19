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

        editor = CatalogEditor(catalog.root)
        try:
            editor.edit(item)
        except RuntimeError as e:
            return CommandResult(success=False, error=str(e))

        return CommandResult(success=True, output=f"Opened '{name}' in editor.")

