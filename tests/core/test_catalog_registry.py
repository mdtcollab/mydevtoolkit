"""Tests for CatalogRegistry."""

from pathlib import Path

import yaml

from mdt.catalog.registry import CatalogRegistry


def _create_item(catalog_root: Path, name: str, kind: str = "skill", **kwargs) -> None:
    """Helper to create a catalog item directory with YAML."""
    item_dir = catalog_root / name
    item_dir.mkdir(parents=True, exist_ok=True)
    (item_dir / "source").mkdir(exist_ok=True)
    data = {
        "name": name,
        "kind": kind,
        "description": kwargs.get("description", f"A {kind}"),
        "tags": kwargs.get("tags", {}),
        "targets": kwargs.get("targets", {}),
        "source": kwargs.get("source", {"files": ["SKILL.md"]}),
    }
    (item_dir / "catalog-item.yaml").write_text(yaml.dump(data))


def test_list_items_multiple(tmp_path: Path) -> None:
    _create_item(tmp_path, "skill-a")
    _create_item(tmp_path, "skill-b")
    registry = CatalogRegistry(catalog_root=tmp_path)
    items = registry.list_items()
    assert len(items) == 2
    assert {i.name for i in items} == {"skill-a", "skill-b"}


def test_list_items_empty_catalog(tmp_path: Path) -> None:
    registry = CatalogRegistry(catalog_root=tmp_path)
    assert registry.list_items() == []


def test_list_items_catalog_not_exists(tmp_path: Path) -> None:
    registry = CatalogRegistry(catalog_root=tmp_path / "nonexistent")
    assert registry.list_items() == []


def test_get_item_exists(tmp_path: Path) -> None:
    _create_item(tmp_path, "openspec-propose")
    registry = CatalogRegistry(catalog_root=tmp_path)
    item = registry.get_item("openspec-propose")
    assert item is not None
    assert item.name == "openspec-propose"


def test_get_item_not_found(tmp_path: Path) -> None:
    registry = CatalogRegistry(catalog_root=tmp_path)
    assert registry.get_item("nonexistent") is None


def test_filter_by_kind(tmp_path: Path) -> None:
    _create_item(tmp_path, "s1", kind="skill")
    _create_item(tmp_path, "i1", kind="instruction")
    _create_item(tmp_path, "a1", kind="agent")
    registry = CatalogRegistry(catalog_root=tmp_path)
    skills = registry.list_items(kind="skill")
    assert len(skills) == 1
    assert skills[0].name == "s1"


def test_filter_by_tag(tmp_path: Path) -> None:
    _create_item(tmp_path, "py-skill", tags={"language": ["python"], "topic": ["testing"]})
    _create_item(tmp_path, "js-skill", tags={"language": ["javascript"]})
    registry = CatalogRegistry(catalog_root=tmp_path)
    py_items = registry.list_items(tag=("language", "python"))
    assert len(py_items) == 1
    assert py_items[0].name == "py-skill"


def test_filter_by_target(tmp_path: Path) -> None:
    _create_item(tmp_path, "claude-skill", targets={
        "claude": {"install_mode": "symlink", "path_template": ".claude/skills/{name}/SKILL.md"},
    })
    _create_item(tmp_path, "copilot-skill", targets={
        "copilot": {"install_mode": "copy", "path_template": ".github/skills/{name}/SKILL.md"},
    })
    registry = CatalogRegistry(catalog_root=tmp_path)
    claude_items = registry.list_items(target="claude")
    assert len(claude_items) == 1
    assert claude_items[0].name == "claude-skill"


def test_filter_by_logical_consumer(tmp_path: Path) -> None:
    _create_item(tmp_path, "shared-skill", targets={
        "shared_claude": {
            "install_mode": "symlink",
            "path_template": ".claude/skills/{name}/SKILL.md",
            "consumers": ["claude", "copilot"],
        },
    })
    registry = CatalogRegistry(catalog_root=tmp_path)
    copilot_items = registry.list_items(target="copilot")
    assert len(copilot_items) == 1
    assert copilot_items[0].name == "shared-skill"


def test_custom_path_via_env(tmp_path: Path, monkeypatch) -> None:
    custom = tmp_path / "custom-catalog"
    custom.mkdir()
    _create_item(custom, "env-skill")
    monkeypatch.setenv("MDT_CATALOG_PATH", str(custom))
    registry = CatalogRegistry()
    items = registry.list_items()
    assert len(items) == 1
    assert items[0].name == "env-skill"


def test_default_path_when_no_env(monkeypatch) -> None:
    monkeypatch.delenv("MDT_CATALOG_PATH", raising=False)
    registry = CatalogRegistry()
    assert registry.root == Path.home() / ".config" / "mdt" / "catalog"

