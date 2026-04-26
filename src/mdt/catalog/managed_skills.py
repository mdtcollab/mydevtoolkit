"""Headless managed-skill discovery, status, and import helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil
from typing import Iterable

import yaml

from mdt.catalog.item import CatalogItem, TargetConfig
from mdt.catalog.manifest import CatalogManifest


@dataclass(frozen=True, slots=True)
class KnownSkillLocation:
    key: str
    root: str
    path_template: str
    consumers: tuple[str, ...]
    install_mode: str


KNOWN_SKILL_LOCATIONS: tuple[KnownSkillLocation, ...] = (
    KnownSkillLocation(
        key="shared_claude",
        root=".claude/skills",
        path_template=".claude/skills/{name}/SKILL.md",
        consumers=("claude", "copilot"),
        install_mode="symlink",
    ),
    KnownSkillLocation(
        key="copilot",
        root=".github/skills",
        path_template=".github/skills/{name}/SKILL.md",
        consumers=("copilot",),
        install_mode="copy",
    ),
)

WORKFLOW_KEYWORDS = (
    "openspec",
    "opsx",
    "speckit",
    "spec-kit",
    "spec kit",
)


@dataclass(slots=True)
class DiscoveredSkill:
    name: str
    directory: Path
    relative_directory: str
    primary_relative_path: str
    files: list[str]
    install_target: str
    logical_consumers: list[str]
    install_mode: str
    content_hash: str
    last_edited_at: str | None
    description: str
    default_selected: bool


@dataclass(slots=True)
class ManagedSkillStatus:
    name: str
    state: str
    central_item: CatalogItem | None
    installed_path: str | None
    install_mode: str | None
    install_target: str | None
    logical_consumers: list[str]
    central_last_edited_at: str | None
    project_last_edited_at: str | None
    central_hash: str | None
    project_hash: str | None
    central_exists: bool
    project_exists: bool
    is_symlink: bool
    default_selected: bool = True


@dataclass(slots=True)
class ImportResult:
    source_name: str
    imported_name: str
    item: CatalogItem
    created_path: Path


def resolve_item_target(item: CatalogItem, requested_target: str) -> tuple[str, TargetConfig] | None:
    target = item.targets.get(requested_target)
    if target is not None:
        return requested_target, target
    for target_name, config in item.targets.items():
        if requested_target in config.consumers:
            return target_name, config
    return None


def item_supports_target(item: CatalogItem, requested_target: str) -> bool:
    return resolve_item_target(item, requested_target) is not None


def _hash_paths(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p)):
        digest.update(str(path.name).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _hash_directory(directory: Path) -> str:
    if directory.is_file():
        return _hash_paths([directory])
    files = [path for path in directory.rglob("*") if path.is_file()]
    return _hash_paths(files)


def _timestamp_for_path(path: Path) -> str | None:
    try:
        if path.is_file() or path.is_symlink():
            stamp = path.lstat().st_mtime if path.is_symlink() else path.stat().st_mtime
            return datetime.fromtimestamp(stamp, timezone.utc).isoformat()
        if path.is_dir():
            latest = max(
                (child.stat().st_mtime for child in path.rglob("*") if child.is_file()),
                default=path.stat().st_mtime,
            )
            return datetime.fromtimestamp(latest, timezone.utc).isoformat()
    except OSError:
        return None
    return None


def _extract_description(skill_dir: Path) -> str:
    primary = skill_dir / "SKILL.md"
    if not primary.is_file():
        return ""
    for line in primary.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
        if stripped:
            return stripped
    return ""


def is_workflow_skill(name: str, skill_dir: Path) -> bool:
    normalized_name = name.lower()
    if any(keyword in normalized_name for keyword in WORKFLOW_KEYWORDS):
        return True
    skill_file = skill_dir / "SKILL.md"
    if skill_file.is_file():
        content = skill_file.read_text().lower()
        return any(keyword in content for keyword in WORKFLOW_KEYWORDS)
    return False


def discover_project_skills(project_root: Path) -> list[DiscoveredSkill]:
    discovered: dict[str, DiscoveredSkill] = {}
    for location in KNOWN_SKILL_LOCATIONS:
        base_dir = project_root / location.root
        if not base_dir.is_dir():
            continue
        for child in sorted(base_dir.iterdir()):
            if not child.is_dir():
                continue
            files = [path for path in child.rglob("*") if path.is_file()]
            if not files:
                continue
            relative_files = [str(path.relative_to(child)) for path in files]
            primary = child / "SKILL.md"
            primary_relative = str(primary.relative_to(project_root)) if primary.is_file() else str(files[0].relative_to(project_root))
            candidate = DiscoveredSkill(
                name=child.name,
                directory=child,
                relative_directory=str(child.relative_to(project_root)),
                primary_relative_path=primary_relative,
                files=sorted(relative_files),
                install_target=location.key,
                logical_consumers=list(location.consumers),
                install_mode=location.install_mode,
                content_hash=_hash_directory(child),
                last_edited_at=_timestamp_for_path(child),
                description=_extract_description(child),
                default_selected=not is_workflow_skill(child.name, child),
            )
            existing = discovered.get(candidate.name)
            if existing is None:
                discovered[candidate.name] = candidate
                continue
            merged_consumers = sorted({*existing.logical_consumers, *candidate.logical_consumers})
            preferred = existing if len(existing.logical_consumers) >= len(candidate.logical_consumers) else candidate
            preferred.logical_consumers = merged_consumers
            preferred.default_selected = existing.default_selected and candidate.default_selected
            discovered[candidate.name] = preferred
    return sorted(discovered.values(), key=lambda skill: skill.name)


def infer_skill_targets(skill: DiscoveredSkill) -> dict[str, dict[str, object]]:
    return {
        skill.install_target: {
            "install_mode": skill.install_mode,
            "path_template": next(
                location.path_template
                for location in KNOWN_SKILL_LOCATIONS
                if location.key == skill.install_target
            ),
            "consumers": skill.logical_consumers,
        }
    }


def import_project_skill(
    project_root: Path,
    catalog_root: Path,
    skill: DiscoveredSkill,
    *,
    rename_to: str | None = None,
    add_prefix: bool = False,
) -> ImportResult:
    imported_name = rename_to or skill.name
    if add_prefix and not imported_name.startswith("mdt-"):
        imported_name = f"mdt-{imported_name}"

    item_dir = catalog_root / imported_name
    source_dir = item_dir / "source"
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    if source_dir.exists():
        shutil.rmtree(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)

    for relative_file in skill.files:
        source = skill.directory / relative_file
        target = source_dir / relative_file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    catalog_yaml = item_dir / "catalog-item.yaml"
    if catalog_yaml.is_file():
        metadata = yaml.safe_load(catalog_yaml.read_text()) or {}
    else:
        metadata = {}
    metadata.update({
        "name": imported_name,
        "kind": "skill",
        "description": metadata.get("description") or skill.description,
        "tags": metadata.get("tags") or {},
        "targets": metadata.get("targets") or infer_skill_targets(skill),
        "source": {"files": skill.files},
    })
    catalog_yaml.write_text(yaml.dump(metadata, sort_keys=False))

    return ImportResult(
        source_name=skill.name,
        imported_name=imported_name,
        item=CatalogItem.from_yaml(catalog_yaml),
        created_path=item_dir,
    )


def build_managed_skill_statuses(
    project_root: Path,
    catalog_root: Path,
    manifest: CatalogManifest | None = None,
) -> list[ManagedSkillStatus]:
    manifest = manifest or CatalogManifest.load(project_root)
    central_items: dict[str, CatalogItem] = {}
    if catalog_root.is_dir():
        for child in sorted(catalog_root.iterdir()):
            yaml_path = child / "catalog-item.yaml"
            if not yaml_path.is_file():
                continue
            try:
                item = CatalogItem.from_yaml(yaml_path)
            except Exception:  # noqa: BLE001
                continue
            if item.kind == "skill":
                central_items[item.name] = item

    project_skills = {skill.name: skill for skill in discover_project_skills(project_root)}
    manifest_records = {record["name"]: record for record in manifest.list_installed()}

    relevant_names = sorted(set(project_skills) | set(manifest_records))
    statuses: list[ManagedSkillStatus] = []
    for name in relevant_names:
        record = manifest_records.get(name)
        central_item = central_items.get(name)
        project_skill = project_skills.get(name)

        installed_path = None
        if record and record.get("installed_path"):
            installed_path = str(record["installed_path"])
        elif project_skill is not None:
            installed_path = project_skill.primary_relative_path

        installed_abspath = project_root / installed_path if installed_path else None
        project_exists = bool(installed_abspath and (installed_abspath.exists() or installed_abspath.is_symlink()))
        is_symlink = bool(installed_abspath and installed_abspath.is_symlink())

        if project_skill is not None:
            project_hash = project_skill.content_hash
            project_last_edited_at = project_skill.last_edited_at
            logical_consumers = list(project_skill.logical_consumers)
            install_target = project_skill.install_target
            install_mode = record.get("install_mode") if record else project_skill.install_mode
        elif installed_abspath and project_exists:
            project_hash = _hash_directory(installed_abspath)
            project_last_edited_at = _timestamp_for_path(installed_abspath)
            logical_consumers = list(record.get("logical_consumers", [])) if record else []
            install_target = record.get("install_target") if record else None
            install_mode = record.get("install_mode") if record else None
        else:
            project_hash = None
            project_last_edited_at = None
            logical_consumers = list(record.get("logical_consumers", [])) if record else []
            install_target = record.get("install_target") if record else None
            install_mode = record.get("install_mode") if record else None

        if central_item is not None:
            central_paths = [catalog_root / central_item.name / "source" / rel for rel in central_item.source_files]
            central_hash = _hash_paths([path for path in central_paths if path.is_file()]) if central_paths else None
            central_last_edited_at = _timestamp_for_path(catalog_root / central_item.name / "source")
            if not logical_consumers and central_item.targets:
                first_target_name, first_target = next(iter(central_item.targets.items()))
                logical_consumers = list(first_target.consumers or [first_target_name])
                install_target = install_target or first_target_name
                install_mode = install_mode or first_target.install_mode
        else:
            central_hash = None
            central_last_edited_at = None

        if central_item is None:
            state = "project only"
        elif record is not None:
            state = manifest.classify_state(
                name,
                central_hash=central_hash or "",
                project_hash=project_hash,
                exists_in_project=project_exists,
                is_symlink=is_symlink,
                central_last_edited_at=central_last_edited_at,
                project_last_edited_at=project_last_edited_at,
            ) or "project only"
        elif project_exists:
            if is_symlink:
                state = "symlinked"
            elif project_hash == central_hash:
                state = "in sync"
            else:
                project_dt = datetime.fromisoformat(project_last_edited_at) if project_last_edited_at else None
                central_dt = datetime.fromisoformat(central_last_edited_at) if central_last_edited_at else None
                if project_dt and central_dt:
                    state = "project newer" if project_dt > central_dt else "central newer"
                else:
                    state = "project newer"
        else:
            state = "missing"

        statuses.append(ManagedSkillStatus(
            name=name,
            state=state,
            central_item=central_item,
            installed_path=installed_path,
            install_mode=install_mode,
            install_target=install_target,
            logical_consumers=logical_consumers,
            central_last_edited_at=central_last_edited_at,
            project_last_edited_at=project_last_edited_at,
            central_hash=central_hash,
            project_hash=project_hash,
            central_exists=central_item is not None,
            project_exists=project_exists,
            is_symlink=is_symlink,
            default_selected=project_skill.default_selected if project_skill else True,
        ))
    return statuses

