"""Catalog editor for opening items in an external editor."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from mdt.catalog.item import CatalogItem
from mdt.core import settings

FALLBACK_EDITORS = ["nano", "vi"]


class CatalogEditor:
    """Opens catalog items in an external editor."""

    def __init__(self, catalog_root: Path) -> None:
        self._catalog_root = catalog_root

    def resolve_editor(self) -> str:
        """Resolve which editor to use. Checks MDT settings, then $EDITOR, then fallbacks."""
        configured = settings.get("editor")
        if configured:
            return configured
        editor = os.environ.get("EDITOR")
        if editor:
            return editor
        for fallback in FALLBACK_EDITORS:
            if shutil.which(fallback):
                return fallback
        raise RuntimeError(
            "No editor found. Set $EDITOR or install nano/vi."
        )

    def resolve_source_path(self, item: CatalogItem | str, primary_file: str | None = None) -> Path:
        """Resolve the canonical source path for the item's primary file."""
        if isinstance(item, str):
            item_name = item
            primary = primary_file or "SKILL.md"
        else:
            item_name = item.name
            primary = primary_file or (item.source_files[0] if item.source_files else "README.md")
        return self._catalog_root / item_name / "source" / primary

    def edit(self, item: CatalogItem) -> None:
        """Open the item's canonical source in an editor."""
        editor = self.resolve_editor()
        source_path = self.resolve_source_path(item)
        # Split editor string to handle args like "code --wait"
        cmd = editor.split() + [str(source_path)]
        subprocess.run(cmd, check=False)

