"""Tests for managed skill discovery, import, and status helpers."""

from pathlib import Path

import yaml

from mdt.catalog.installer import CatalogInstaller
from mdt.catalog.item import CatalogItem, TargetConfig
from mdt.catalog.managed_skills import (
    build_managed_skill_statuses,
    discover_project_skills,
    import_project_skill,
)
from mdt.catalog.manifest import CatalogManifest


def _write_project_skill(project_root: Path, root: str, name: str, content: str) -> Path:
    skill_dir = project_root / root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(content)
    return skill_dir


def _create_central_item(catalog_root: Path, name: str, *, target_key: str = "copilot") -> CatalogItem:
    if target_key == "shared_claude":
        targets = {
            "shared_claude": TargetConfig(
                install_mode="symlink",
                path_template=".claude/skills/{name}/SKILL.md",
                consumers=["claude", "copilot"],
            )
        }
    else:
        targets = {
            "copilot": TargetConfig(
                install_mode="copy",
                path_template=".github/skills/{name}/SKILL.md",
                consumers=["copilot"],
            )
        }
    source_dir = catalog_root / name / "source"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text(f"# {name}\n\nInitial content")
    data = {
        "name": name,
        "kind": "skill",
        "description": f"{name} description",
        "tags": {},
        "targets": {
            key: {
                "install_mode": value.install_mode,
                "path_template": value.path_template,
                "consumers": value.consumers,
            }
            for key, value in targets.items()
        },
        "source": {"files": ["SKILL.md"]},
    }
    (catalog_root / name / "catalog-item.yaml").write_text(yaml.dump(data))
    return CatalogItem.from_yaml(catalog_root / name / "catalog-item.yaml")


def test_discover_project_skills_known_locations_and_selection_defaults(tmp_path: Path) -> None:
    _write_project_skill(tmp_path, ".github/skills", "review-helper", "# Review Helper\n")
    _write_project_skill(tmp_path, ".claude/skills", "openspec-propose", "# OpenSpec Propose\n")

    discovered = discover_project_skills(tmp_path)
    by_name = {skill.name: skill for skill in discovered}

    assert by_name["review-helper"].logical_consumers == ["copilot"]
    assert by_name["review-helper"].default_selected is True
    assert by_name["openspec-propose"].logical_consumers == ["claude", "copilot"]
    assert by_name["openspec-propose"].default_selected is False


def test_import_project_skill_supports_rename_and_prefix(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    skill_dir = _write_project_skill(tmp_path, ".github/skills", "review-helper", "# Review Helper\n")
    discovered = discover_project_skills(tmp_path)
    skill = next(skill for skill in discovered if skill.name == "review-helper")

    result = import_project_skill(tmp_path, catalog_root, skill, rename_to="review", add_prefix=True)

    assert result.imported_name == "mdt-review"
    assert (catalog_root / "mdt-review" / "source" / "SKILL.md").read_text() == (skill_dir / "SKILL.md").read_text()
    assert result.item.targets["copilot"].resolve_path("mdt-review") == ".github/skills/mdt-review/SKILL.md"


def test_build_managed_skill_statuses_reports_central_newer(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _create_central_item(catalog_root, "review-helper")

    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="copilot", project_root=project_root, manifest=manifest)
    (catalog_root / "review-helper" / "source" / "SKILL.md").write_text("# review-helper\n\nUpdated central content")

    status = next(status for status in build_managed_skill_statuses(project_root, catalog_root, manifest) if status.name == "review-helper")
    assert status.state == "central newer"


def test_build_managed_skill_statuses_reports_project_newer(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _create_central_item(catalog_root, "review-helper")

    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="copilot", project_root=project_root, manifest=manifest)
    (project_root / ".github" / "skills" / "review-helper" / "SKILL.md").write_text("# review-helper\n\nUpdated project content")

    status = next(status for status in build_managed_skill_statuses(project_root, catalog_root, manifest) if status.name == "review-helper")
    assert status.state == "project newer"


def test_build_managed_skill_statuses_reports_symlinked(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _create_central_item(catalog_root, "review-helper", target_key="shared_claude")

    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="claude", project_root=project_root, manifest=manifest)

    status = next(status for status in build_managed_skill_statuses(project_root, catalog_root, manifest) if status.name == "review-helper")
    assert status.state == "symlinked"
    assert status.logical_consumers == ["claude", "copilot"]


def test_build_managed_skill_statuses_reports_missing(tmp_path: Path) -> None:
    catalog_root = tmp_path / "catalog"
    project_root = tmp_path / "project"
    project_root.mkdir()
    item = _create_central_item(catalog_root, "review-helper")

    manifest = CatalogManifest()
    installer = CatalogInstaller(catalog_root)
    installer.install(item, target="copilot", project_root=project_root, manifest=manifest)
    (project_root / ".github" / "skills" / "review-helper" / "SKILL.md").unlink()

    status = next(status for status in build_managed_skill_statuses(project_root, catalog_root, manifest) if status.name == "review-helper")
    assert status.state == "missing"

