"""Tests for CatalogItem and TargetConfig."""

from pathlib import Path

import pytest
import yaml

from mdt.catalog.item import CatalogItem, TargetConfig


def test_target_config_resolve_path() -> None:
    tc = TargetConfig(install_mode="symlink", path_template=".claude/skills/{name}/SKILL.md")
    assert tc.resolve_path("my-skill") == ".claude/skills/my-skill/SKILL.md"


def test_catalog_item_creation_all_fields() -> None:
    item = CatalogItem(
        name="openspec-propose",
        kind="skill",
        description="Propose a change",
        tags={"language": ["python"], "topic": ["openspec"]},
        targets={
            "shared_claude": TargetConfig(
                install_mode="symlink",
                path_template=".claude/skills/{name}/SKILL.md",
                consumers=["claude", "copilot"],
            ),
        },
        source={"files": ["SKILL.md"]},
    )
    assert item.name == "openspec-propose"
    assert item.kind == "skill"
    assert item.source_files == ["SKILL.md"]
    assert item.targets["shared_claude"].install_mode == "symlink"
    assert item.targets["shared_claude"].consumers == ["claude", "copilot"]


def test_catalog_item_no_language_tags() -> None:
    item = CatalogItem(name="test", kind="instruction", tags={"topic": ["testing"]})
    assert item.tags.get("language", []) == []


def test_catalog_item_from_yaml(tmp_path: Path) -> None:
    data = {
        "name": "my-skill",
        "kind": "skill",
        "description": "A test skill",
        "tags": {"language": ["python"], "topic": ["testing"]},
        "targets": {
            "claude": {"install_mode": "symlink", "path_template": ".claude/skills/{name}/SKILL.md"},
            "shared_claude": {
                "install_mode": "symlink",
                "path_template": ".claude/skills/{name}/SKILL.md",
                "consumers": ["claude", "copilot"],
            },
        },
        "source": {"files": ["SKILL.md"]},
    }
    yaml_path = tmp_path / "catalog-item.yaml"
    yaml_path.write_text(yaml.dump(data))

    item = CatalogItem.from_yaml(yaml_path)
    assert item.name == "my-skill"
    assert item.kind == "skill"
    assert item.targets["claude"].install_mode == "symlink"
    assert item.targets["claude"].consumers == ["claude"]
    assert item.targets["shared_claude"].resolve_path("my-skill") == ".claude/skills/my-skill/SKILL.md"
    assert item.targets["shared_claude"].consumers == ["claude", "copilot"]
    assert item.source_files == ["SKILL.md"]


def test_catalog_item_from_yaml_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        CatalogItem.from_yaml(Path("/nonexistent/catalog-item.yaml"))

