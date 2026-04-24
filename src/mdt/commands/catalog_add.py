"""catalog_add command: scaffold a new catalog item."""

from __future__ import annotations

from pathlib import Path

import yaml

from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogAddCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        if not args:
            return CommandResult(success=False, error="Usage: catalog add <name> --kind <kind>")

        name = args[0]
        kind = "instruction"  # default
        for i, arg in enumerate(args):
            if arg == "--kind" and i + 1 < len(args):
                kind = args[i + 1]
                break

        catalog = CatalogRegistry()
        item_dir = catalog.root / name

        if item_dir.exists():
            return CommandResult(success=False, error=f"Catalog item '{name}' already exists.")

        # Scaffold
        item_dir.mkdir(parents=True)
        source_dir = item_dir / "source"
        source_dir.mkdir()

        metadata = {
            "name": name,
            "kind": kind,
            "description": "",
            "tags": {},
            "targets": {},
            "source": {"files": []},
        }
        (item_dir / "catalog-item.yaml").write_text(yaml.dump(metadata, default_flow_style=False))

        return CommandResult(
            success=True,
            output=f"Created catalog item '{name}' [{kind}] at {item_dir}",
        )

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        if position == 1:
            prefix = tokens[1].lower() if len(tokens) > 1 else ""
            return [f for f in ["--kind"] if f.startswith(prefix)]
        if position == 2:
            prefix = tokens[2].lower() if len(tokens) > 2 else ""
            kinds = ["agent", "instruction", "prompt", "skill"]
            return [k for k in kinds if k.startswith(prefix)]
        return []

