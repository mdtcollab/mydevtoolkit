"""Tests for catalog commands."""

from pathlib import Path
from unittest.mock import patch

import yaml

from mdt.catalog.manifest import CatalogManifest
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry

from mdt.commands.catalog_add import CatalogAddCommand
from mdt.commands.catalog_edit import CatalogEditCommand
from mdt.commands.catalog_help import CatalogHelpCommand
from mdt.commands.catalog_import import CatalogImportCommand
from mdt.commands.catalog_install import CatalogInstallCommand
from mdt.commands.catalog_list import CatalogListCommand
from mdt.commands.catalog_remove import CatalogRemoveCommand
from mdt.commands.catalog_status import CatalogStatusCommand
from mdt.commands.catalog_sync import CatalogSyncCommand


def _ctx(tmp_path: Path) -> ProjectContext:
    return ProjectContext(cwd=tmp_path, repo_root=tmp_path, project_name="test")


def _registry() -> CommandRegistry:
    return CommandRegistry()


def _create_catalog_item(catalog_root: Path, name: str, kind: str = "skill") -> None:
    item_dir = catalog_root / name
    source_dir = item_dir / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text(f"# {name}")
    data = {
        "name": name,
        "kind": kind,
        "description": f"A {kind} called {name}",
        "tags": {},
        "targets": {
            "claude": {"install_mode": "copy", "path_template": ".claude/skills/{name}/SKILL.md"},
        },
        "source": {"files": ["SKILL.md"]},
    }
    (item_dir / "catalog-item.yaml").write_text(yaml.dump(data))


def _create_project_skill(project_root: Path, root: str, name: str, content: str = "# Skill\n") -> None:
    skill_dir = project_root / root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(content)


# --- CatalogListCommand ---

def test_catalog_list_empty(tmp_path: Path) -> None:
    with patch("mdt.commands.catalog_list.CatalogRegistry") as mock_registry:
        mock_registry.return_value.list_items.return_value = []
        cmd = CatalogListCommand(_registry())
        result = cmd([], _ctx(tmp_path))
        assert result.success
        assert "empty" in result.output.lower()


def test_catalog_list_with_items(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    _create_catalog_item(catalog_root, "my-skill")
    with patch("mdt.commands.catalog_list.CatalogRegistry") as mock_registry:
        from mdt.catalog.registry import CatalogRegistry

        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogListCommand(_registry())
        result = cmd([], _ctx(tmp_path))
        assert result.success
        assert "my-skill" in result.output


# --- CatalogAddCommand ---

def test_catalog_add_success(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    catalog_root.mkdir()
    with patch("mdt.commands.catalog_add.CatalogRegistry") as mock_registry:
        mock_registry.return_value.root = catalog_root
        cmd = CatalogAddCommand(_registry())
        result = cmd(["new-skill", "--kind", "skill"], _ctx(tmp_path))
        assert result.success
        assert (catalog_root / "new-skill" / "catalog-item.yaml").is_file()


def test_catalog_add_already_exists(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    _create_catalog_item(catalog_root, "existing")
    with patch("mdt.commands.catalog_add.CatalogRegistry") as mock_registry:
        mock_registry.return_value.root = catalog_root
        cmd = CatalogAddCommand(_registry())
        result = cmd(["existing", "--kind", "skill"], _ctx(tmp_path))
        assert not result.success
        assert "already exists" in result.error


def test_catalog_add_no_args(tmp_path: Path) -> None:
    cmd = CatalogAddCommand(_registry())
    result = cmd([], _ctx(tmp_path))
    assert not result.success


# --- CatalogInstallCommand ---

def test_catalog_install_success(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _create_catalog_item(catalog_root, "my-skill")

    with patch("mdt.commands.catalog_install.CatalogRegistry") as mock_registry:
        from mdt.catalog.registry import CatalogRegistry

        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogInstallCommand(_registry())
        result = cmd(["my-skill", "--target", "claude"], _ctx(project_root))
        assert result.success
        assert "Installed" in result.output


def test_catalog_install_shared_target_success(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item_dir = catalog_root / "shared-skill"
    source_dir = item_dir / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text("# shared")
    (item_dir / "catalog-item.yaml").write_text(yaml.dump({
        "name": "shared-skill",
        "kind": "skill",
        "description": "shared skill",
        "tags": {},
        "targets": {
            "shared_claude": {
                "install_mode": "symlink",
                "path_template": ".claude/skills/{name}/SKILL.md",
                "consumers": ["claude", "copilot"],
            }
        },
        "source": {"files": ["SKILL.md"]},
    }))

    with patch("mdt.commands.catalog_install.CatalogRegistry") as mock_registry:
        from mdt.catalog.registry import CatalogRegistry

        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogInstallCommand(_registry())
        result = cmd(["shared-skill", "--target", "shared_claude"], _ctx(project_root))
        assert result.success
        assert (project_root / ".claude" / "skills" / "shared-skill" / "SKILL.md").exists()


def test_catalog_install_not_found(tmp_path: Path) -> None:
    with patch("mdt.commands.catalog_install.CatalogRegistry") as mock_registry:
        mock_registry.return_value.get_item.return_value = None
        cmd = CatalogInstallCommand(_registry())
        result = cmd(["nonexistent", "--target", "claude"], _ctx(tmp_path))
        assert not result.success
        assert "not found" in result.error


def test_catalog_install_no_target(tmp_path: Path) -> None:
    cmd = CatalogInstallCommand(_registry())
    result = cmd(["my-skill"], _ctx(tmp_path))
    assert not result.success
    assert "--target" in result.error


# --- CatalogRemoveCommand ---

def test_catalog_remove_success(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    installed = project_root / ".claude" / "skills" / "my-skill" / "SKILL.md"
    installed.parent.mkdir(parents=True)
    installed.write_text("content")
    manifest = CatalogManifest()
    manifest.record_install(
        name="my-skill",
        kind="skill",
        target="claude",
        install_mode="copy",
        installed_path=".claude/skills/my-skill/SKILL.md",
        source_hash="abc",
    )
    manifest.save(project_root)

    cmd = CatalogRemoveCommand(_registry())
    result = cmd(["my-skill"], _ctx(project_root))
    assert result.success
    assert not installed.exists()


def test_catalog_remove_not_installed(tmp_path: Path) -> None:
    cmd = CatalogRemoveCommand(_registry())
    result = cmd(["nonexistent"], _ctx(tmp_path))
    assert not result.success
    assert "not installed" in result.error


# --- CatalogSyncCommand ---

def test_catalog_sync_no_items(tmp_path: Path) -> None:
    cmd = CatalogSyncCommand(_registry())
    result = cmd([], _ctx(tmp_path))
    assert result.success
    assert "No catalog items" in result.output


def test_catalog_sync_up_to_date(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _create_catalog_item(catalog_root, "my-skill")

    from mdt.catalog.installer import CatalogInstaller
    from mdt.catalog.registry import CatalogRegistry

    reg = CatalogRegistry(catalog_root=catalog_root)
    item = reg.get_item("my-skill")
    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="claude", project_root=project_root, manifest=manifest)
    manifest.save(project_root)

    with patch("mdt.commands.catalog_sync.CatalogRegistry") as mock_registry:
        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogSyncCommand(_registry())
        result = cmd([], _ctx(project_root))
        assert result.success
        assert "up to date" in result.output


def test_catalog_sync_reports_project_newer(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _create_catalog_item(catalog_root, "my-skill")

    from mdt.catalog.installer import CatalogInstaller
    from mdt.catalog.registry import CatalogRegistry

    reg = CatalogRegistry(catalog_root=catalog_root)
    item = reg.get_item("my-skill")
    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="claude", project_root=project_root, manifest=manifest)
    manifest.save(project_root)

    installed_path = project_root / ".claude" / "skills" / "my-skill" / "SKILL.md"
    if installed_path.is_symlink():
        installed_path.unlink()
    installed_path.write_text("# project newer")

    with patch("mdt.commands.catalog_sync.CatalogRegistry") as mock_registry:
        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogSyncCommand(_registry())
        result = cmd([], _ctx(project_root))
        assert result.success
        assert "project newer" in result.output


# --- CatalogImportCommand ---

def test_catalog_import_preview_shows_default_selection(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    _create_project_skill(tmp_path, ".github/skills", "review-helper")
    _create_project_skill(tmp_path, ".claude/skills", "openspec-propose", "# OpenSpec Propose\n")

    with patch("mdt.commands.catalog_import.CatalogRegistry") as mock_registry:
        from mdt.catalog.registry import CatalogRegistry

        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogImportCommand(_registry())
        result = cmd([], _ctx(tmp_path))
        assert result.success
        assert "[x] review-helper" in result.output
        assert "[ ] openspec-propose" in result.output


def test_catalog_import_supports_prefix_and_rename(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    _create_project_skill(tmp_path, ".github/skills", "review-helper", "# Review Helper\n")

    with patch("mdt.commands.catalog_import.CatalogRegistry") as mock_registry:
        from mdt.catalog.registry import CatalogRegistry

        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogImportCommand(_registry())
        result = cmd(["review-helper", "--as", "review", "--prefix"], _ctx(tmp_path))
        assert result.success
        assert "review-helper -> mdt-review" in result.output
        assert (catalog_root / "mdt-review" / "catalog-item.yaml").is_file()


# --- CatalogStatusCommand ---

def test_catalog_status_shows_managed_skill_details(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _create_catalog_item(catalog_root, "my-skill")

    from mdt.catalog.installer import CatalogInstaller
    from mdt.catalog.registry import CatalogRegistry

    reg = CatalogRegistry(catalog_root=catalog_root)
    item = reg.get_item("my-skill")
    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="claude", project_root=project_root, manifest=manifest)

    with patch("mdt.commands.catalog_status.CatalogRegistry") as mock_registry:
        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        cmd = CatalogStatusCommand(_registry())
        result = cmd([], _ctx(project_root))
        assert result.success
        assert "my-skill" in result.output
        assert "mode:" in result.output
        assert "consumers:" in result.output


# --- CatalogHelpCommand ---

def test_catalog_help_mentions_import_and_status(tmp_path: Path) -> None:
    cmd = CatalogHelpCommand(_registry())
    result = cmd([], _ctx(tmp_path))
    assert result.success
    assert "catalog import" in result.output
    assert "catalog status" in result.output


# --- CatalogEditCommand ---

def test_catalog_edit_success_from_manifest_context(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _create_catalog_item(catalog_root, "my-skill")

    manifest = CatalogManifest()
    manifest.record_install(
        name="my-skill",
        kind="skill",
        target="claude",
        install_mode="copy",
        installed_path=".claude/skills/my-skill/SKILL.md",
        source_hash="abc",
    )
    manifest.save(project_root)

    with patch("mdt.commands.catalog_edit.CatalogRegistry") as mock_registry:
        from mdt.catalog.registry import CatalogRegistry

        mock_registry.return_value = CatalogRegistry(catalog_root=catalog_root)
        with patch("mdt.commands.catalog_edit.CatalogEditor.resolve_editor", return_value="vim"):
            cmd = CatalogEditCommand(_registry())
            result = cmd(["my-skill"], _ctx(project_root))
            assert result.success
            assert result.data["run_external"][-1].endswith("catalog/my-skill/source/SKILL.md")


def test_catalog_edit_not_found(tmp_path: Path) -> None:
    with patch("mdt.commands.catalog_edit.CatalogRegistry") as mock_registry:
        mock_registry.return_value.get_item.return_value = None
        cmd = CatalogEditCommand(_registry())
        result = cmd(["nonexistent"], _ctx(tmp_path))
        assert not result.success
        assert "not found" in result.error


def test_catalog_edit_no_args(tmp_path: Path) -> None:
    cmd = CatalogEditCommand(_registry())
    result = cmd([], _ctx(tmp_path))
    assert not result.success

