"""Tests for catalog command registration in build_command_registry()."""

from mdt.commands import build_command_registry


def test_catalog_commands_registered_under_catalog_category() -> None:
    registry = build_command_registry()
    expected = {
        "catalog_list", "catalog_add", "catalog_install",
        "catalog_remove", "catalog_sync", "catalog_edit",
    }
    all_cmds = registry.all()
    catalog_cmds = {name for name, _, cat in all_cmds if cat == "catalog"}
    assert catalog_cmds == expected


def test_catalog_category_declared() -> None:
    registry = build_command_registry()
    assert "catalog" in registry.categories()

