"""Tests for CatalogInstaller."""

from pathlib import Path
from unittest.mock import patch

import yaml

from mdt.catalog.installer import CatalogInstaller
from mdt.catalog.item import CatalogItem, TargetConfig
from mdt.catalog.manifest import CatalogManifest
from mdt.catalog.renderer import CatalogRenderer

import pytest


def _setup_catalog_item(catalog_root: Path, name: str = "my-skill", files: list[str] | None = None) -> CatalogItem:
    """Create a catalog item on disk and return the model."""
    files = files or ["SKILL.md"]
    source_dir = catalog_root / name / "source"
    source_dir.mkdir(parents=True)
    for f in files:
        (source_dir / f).write_text(f"Content of {f}")

    return CatalogItem(
        name=name,
        kind="skill",
        targets={
            "claude": TargetConfig(install_mode="symlink", path_template=".claude/skills/{name}/SKILL.md"),
            "copilot": TargetConfig(install_mode="copy", path_template=".github/skills/{name}/SKILL.md"),
            "opencode": TargetConfig(install_mode="render", path_template=".opencode/agents/{name}.md"),
        },
        source={"files": files},
    )


def test_symlink_install(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _setup_catalog_item(catalog_root)

    installer = CatalogInstaller(catalog_root)
    mode = installer.install(item, target="claude", project_root=project_root)

    target_path = project_root / ".claude" / "skills" / "my-skill" / "SKILL.md"
    assert target_path.is_symlink()
    assert target_path.read_text() == "Content of SKILL.md"
    assert mode == "symlink"


def test_copy_install(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _setup_catalog_item(catalog_root)

    installer = CatalogInstaller(catalog_root)
    mode = installer.install(item, target="copilot", project_root=project_root)

    target_path = project_root / ".github" / "skills" / "my-skill" / "SKILL.md"
    assert target_path.is_file()
    assert not target_path.is_symlink()
    assert target_path.read_text() == "Content of SKILL.md"
    assert mode == "copy"


def test_render_install(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _setup_catalog_item(catalog_root)

    renderer = CatalogRenderer()
    renderer.register("opencode", lambda c, p, i: f"RENDERED: {c}")

    installer = CatalogInstaller(catalog_root, renderer=renderer)
    mode = installer.install(item, target="opencode", project_root=project_root)

    target_path = project_root / ".opencode" / "agents" / "my-skill.md"
    assert target_path.read_text() == "RENDERED: Content of SKILL.md"
    assert mode == "render"


def test_unsupported_target_raises(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _setup_catalog_item(catalog_root)

    installer = CatalogInstaller(catalog_root)
    with pytest.raises(ValueError, match="does not support target 'unsupported'"):
        installer.install(item, target="unsupported", project_root=project_root)


def test_symlink_fallback_to_copy(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _setup_catalog_item(catalog_root)

    installer = CatalogInstaller(catalog_root)
    # Patch _can_symlink to return False
    with patch("mdt.catalog.installer._can_symlink", return_value=False):
        mode = installer.install(item, target="claude", project_root=project_root)

    target_path = project_root / ".claude" / "skills" / "my-skill" / "SKILL.md"
    assert target_path.is_file()
    assert not target_path.is_symlink()
    assert mode == "copy"


def test_manifest_updated_after_install(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _setup_catalog_item(catalog_root)

    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="copilot", project_root=project_root, manifest=manifest)

    record = manifest.get("my-skill")
    assert record is not None
    assert record["kind"] == "skill"
    assert record["target"] == "copilot"
    assert record["install_target"] == "copilot"
    assert record["install_mode"] == "copy"
    assert record["logical_consumers"] == ["copilot"]
    assert record["source_hash"] != ""
    assert record["installed_hash"] != ""


def test_install_resolves_shared_target_by_logical_consumer(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = CatalogItem(
        name="shared-skill",
        kind="skill",
        targets={
            "shared_claude": TargetConfig(
                install_mode="symlink",
                path_template=".claude/skills/{name}/SKILL.md",
                consumers=["claude", "copilot"],
            ),
        },
        source={"files": ["SKILL.md"]},
    )
    source_dir = catalog_root / "shared-skill" / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text("Shared content")

    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    mode = installer.install(item, target="claude", project_root=project_root, manifest=manifest)

    target_path = project_root / ".claude" / "skills" / "shared-skill" / "SKILL.md"
    record = manifest.get("shared-skill")
    assert mode == "symlink"
    assert target_path.is_symlink()
    assert record is not None
    assert record["install_target"] == "shared_claude"
    assert record["logical_consumers"] == ["claude", "copilot"]


def test_multi_file_install(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _setup_catalog_item(catalog_root, files=["SKILL.md", "helpers.py"])

    installer = CatalogInstaller(catalog_root)
    mode = installer.install(item, target="copilot", project_root=project_root)

    base = project_root / ".github" / "skills" / "my-skill"
    assert (base / "SKILL.md").is_file()
    assert (base / "helpers.py").is_file()
    assert mode == "copy"

