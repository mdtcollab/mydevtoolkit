"""Tests for CatalogEditor."""

from pathlib import Path
from unittest.mock import patch

import pytest

from mdt.catalog.editor import CatalogEditor
from mdt.catalog.item import CatalogItem


def _clear_settings():
    """Patch settings.get to return None so env/fallback chain is tested."""
    return patch("mdt.catalog.editor.settings.get", return_value=None)


def test_resolve_editor_from_settings(tmp_path: Path) -> None:
    with patch("mdt.catalog.editor.settings") as mock_settings:
        mock_settings.get.return_value = "micro"
        editor = CatalogEditor(tmp_path)
        assert editor.resolve_editor() == "micro"


def test_resolve_editor_from_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("EDITOR", "code")
    with patch("mdt.catalog.editor.settings") as mock_settings:
        mock_settings.get.return_value = None
        editor = CatalogEditor(tmp_path)
        assert editor.resolve_editor() == "code"


def test_resolve_editor_fallback(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EDITOR", raising=False)
    with patch("mdt.catalog.editor.settings") as mock_settings:
        mock_settings.get.return_value = None
        editor = CatalogEditor(tmp_path)
        result = editor.resolve_editor()
        assert result in ("nano", "vi")


def test_resolve_editor_none_available(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr("shutil.which", lambda _: None)
    with patch("mdt.catalog.editor.settings") as mock_settings:
        mock_settings.get.return_value = None
        editor = CatalogEditor(tmp_path)
        with pytest.raises(RuntimeError, match="No editor found"):
            editor.resolve_editor()


def test_resolve_source_path(tmp_path: Path) -> None:
    item = CatalogItem(name="my-skill", kind="skill", source={"files": ["SKILL.md"]})
    editor = CatalogEditor(tmp_path)
    path = editor.resolve_source_path(item)
    assert path == tmp_path / "my-skill" / "source" / "SKILL.md"

