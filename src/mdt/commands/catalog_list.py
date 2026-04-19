"""catalog_list command: list catalog items with optional filters."""

from __future__ import annotations

from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogListCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        kind = None
        target = None
        tag = None

        # Parse args: --kind <k>, --target <t>, --language <l>, --topic <t>
        i = 0
        while i < len(args):
            if args[i] == "--kind" and i + 1 < len(args):
                kind = args[i + 1]
                i += 2
            elif args[i] == "--target" and i + 1 < len(args):
                target = args[i + 1]
                i += 2
            elif args[i] == "--language" and i + 1 < len(args):
                tag = ("language", args[i + 1])
                i += 2
            elif args[i] == "--topic" and i + 1 < len(args):
                tag = ("topic", args[i + 1])
                i += 2
            else:
                i += 1

        catalog = CatalogRegistry()
        items = catalog.list_items(kind=kind, target=target, tag=tag)

        if not items:
            return CommandResult(success=True, output="Catalog is empty.")

        lines = ["Catalog items:", ""]
        for item in items:
            lines.append(f"  {item.name} [{item.kind}] - {item.description}")

        return CommandResult(success=True, output="\n".join(lines))

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        # Determine if we're at a flag or a value position
        # Flags: --kind, --target, --language, --topic
        # After a flag, offer its values
        if position > 0 and position <= len(tokens):
            prev = tokens[position - 1].lower() if position - 1 < len(tokens) else ""
            prefix = tokens[position].lower() if position < len(tokens) else ""
            if prev == "--kind":
                kinds = ["agent", "instruction", "prompt", "skill"]
                return [k for k in kinds if k.startswith(prefix)]
            if prev == "--target":
                targets = ["claude", "copilot", "opencode"]
                return [t for t in targets if t.startswith(prefix)]

        # Otherwise offer flags
        prefix = tokens[position].lower() if position < len(tokens) else ""
        flags = ["--kind", "--language", "--target", "--topic"]
        return [f for f in flags if f.startswith(prefix)]
