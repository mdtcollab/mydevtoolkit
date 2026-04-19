"""Tests for CatalogEditor."""

from pathlib import Path

import pytest

from mdt.catalog.editor import CatalogEditor
from mdt.catalog.item import CatalogItem


def test_resolve_editor_from_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("EDITOR", "code")
    editor = CatalogEditor(tmp_path)
    assert editor.resolve_editor() == "code"


def test_resolve_editor_fallback(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EDITOR", raising=False)
    # nano or vi should be available on most Linux systems
    editor = CatalogEditor(tmp_path)
    result = editor.resolve_editor()
    assert result in ("nano", "vi")


def test_resolve_editor_none_available(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr("shutil.which", lambda _: None)
    editor = CatalogEditor(tmp_path)
    with pytest.raises(RuntimeError, match="No editor found"):
        editor.resolve_editor()


def test_resolve_source_path(tmp_path: Path) -> None:
    item = CatalogItem(name="my-skill", kind="skill", source={"files": ["SKILL.md"]})
    editor = CatalogEditor(tmp_path)
    path = editor.resolve_source_path(item)
    assert path == tmp_path / "my-skill" / "source" / "SKILL.md"

