"""Tests for CatalogManifest."""

from pathlib import Path

from mdt.catalog.manifest import CatalogManifest


def test_load_nonexistent_returns_empty(tmp_path: Path) -> None:
    manifest = CatalogManifest.load(tmp_path)
    assert manifest.list_installed() == []


def test_save_and_load(tmp_path: Path) -> None:
    manifest = CatalogManifest()
    manifest.record_install(
        name="my-skill", kind="skill", target="claude",
        install_mode="symlink", installed_path=".claude/skills/my-skill/SKILL.md",
        source_hash="abc123",
    )
    manifest.save(tmp_path)
    assert (tmp_path / ".mdt" / "catalog.json").is_file()

    loaded = CatalogManifest.load(tmp_path)
    record = loaded.get("my-skill")
    assert record is not None
    assert record["kind"] == "skill"
    assert record["source_hash"] == "abc123"


def test_record_and_get(tmp_path: Path) -> None:
    manifest = CatalogManifest()
    manifest.record_install(
        name="test", kind="instruction", target="copilot",
        install_mode="copy", installed_path=".github/test.md",
        source_hash="def456",
    )
    record = manifest.get("test")
    assert record is not None
    assert record["target"] == "copilot"
    assert "installed_at" in record


def test_remove_existing() -> None:
    manifest = CatalogManifest()
    manifest.record_install(
        name="x", kind="skill", target="claude",
        install_mode="copy", installed_path="p", source_hash="h",
    )
    manifest.remove("x")
    assert manifest.get("x") is None


def test_remove_nonexistent_no_error() -> None:
    manifest = CatalogManifest()
    manifest.remove("nonexistent")  # Should not raise


def test_check_drift_unchanged() -> None:
    manifest = CatalogManifest()
    manifest.record_install(
        name="s", kind="skill", target="claude",
        install_mode="symlink", installed_path="p", source_hash="abc",
    )
    assert manifest.check_drift("s", "abc") is False


def test_check_drift_changed() -> None:
    manifest = CatalogManifest()
    manifest.record_install(
        name="s", kind="skill", target="claude",
        install_mode="symlink", installed_path="p", source_hash="abc",
    )
    assert manifest.check_drift("s", "xyz") is True


def test_list_installed_multiple() -> None:
    manifest = CatalogManifest()
    for i in range(3):
        manifest.record_install(
            name=f"item-{i}", kind="skill", target="claude",
            install_mode="copy", installed_path=f"p{i}", source_hash=f"h{i}",
        )
    installed = manifest.list_installed()
    assert len(installed) == 3
    assert all("name" in r for r in installed)

