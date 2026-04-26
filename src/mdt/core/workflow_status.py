"""Workflow inspection helpers for OpenSpec and Spec Kit projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

WorkflowType = Literal["openspec", "speckit", "both", "none"]


@dataclass(slots=True)
class WorkflowStatus:
    workflow_type: WorkflowType
    current_change: str | None = None
    current_iteration: str | None = None
    last_command: str | None = None
    next_command: str | None = None


def detect_workflow_status(project_root: str | Path) -> WorkflowStatus:
    root = Path(project_root)
    has_openspec = _has_openspec_markers(root)
    has_speckit = _has_speckit_markers(root)

    if has_openspec and has_speckit:
        return WorkflowStatus(workflow_type="both")
    if has_openspec:
        return _infer_openspec_status(root)
    if has_speckit:
        return _infer_speckit_status(root)
    return WorkflowStatus(workflow_type="none")


def _has_openspec_markers(root: Path) -> bool:
    openspec_root = root / "openspec"
    return openspec_root.is_dir() and any(
        path.exists()
        for path in (
            openspec_root / "config.yaml",
            openspec_root / "changes",
            openspec_root / "specs",
        )
    )


def _has_speckit_markers(root: Path) -> bool:
    return any(path.exists() for path in _speckit_markers(root))


def _speckit_markers(root: Path) -> tuple[Path, ...]:
    return (
        root / ".specify",
        root / "speckit",
        root / ".speckit",
        root / "speckit.yaml",
        root / ".speckit.yaml",
        root / "speckit.json",
        root / ".speckit.json",
    )


def _infer_openspec_status(root: Path) -> WorkflowStatus:
    change_dir = _latest_active_openspec_change(root)
    if change_dir is None:
        return WorkflowStatus(
            workflow_type="openspec",
            last_command="/opsx:archive",
            next_command="/opsx:propose",
        )

    tasks = _task_progress(change_dir / "tasks.md")
    proposal_done = (change_dir / "proposal.md").is_file()
    design_done = (change_dir / "design.md").is_file()
    specs_done = any((change_dir / "specs").glob("**/*.md"))

    if tasks is not None and tasks[1] == tasks[0] and tasks[0] > 0:
        return WorkflowStatus(
            workflow_type="openspec",
            current_change=change_dir.name,
            last_command="/opsx:apply",
            next_command="/opsx:archive",
        )

    if tasks is not None and tasks[1] > 0:
        return WorkflowStatus(
            workflow_type="openspec",
            current_change=change_dir.name,
            last_command="/opsx:apply",
            next_command="/opsx:apply",
        )

    if proposal_done and design_done and specs_done and tasks is not None:
        return WorkflowStatus(
            workflow_type="openspec",
            current_change=change_dir.name,
            last_command="/opsx:propose",
            next_command="/opsx:apply",
        )

    return WorkflowStatus(
        workflow_type="openspec",
        current_change=change_dir.name,
        last_command="/opsx:propose",
        next_command="/opsx:propose",
    )


def _latest_active_openspec_change(root: Path) -> Path | None:
    changes_dir = root / "openspec" / "changes"
    if not changes_dir.is_dir():
        return None

    subdirs = [d for d in changes_dir.iterdir() if d.is_dir() and d.name != "archive"]
    if not subdirs:
        return None
    return max(subdirs, key=lambda d: d.stat().st_mtime)


def _infer_speckit_status(root: Path) -> WorkflowStatus:
    iteration_dir = _latest_speckit_iteration(root)
    if iteration_dir is None:
        return WorkflowStatus(
            workflow_type="speckit",
            last_command="/speckit.init",
            next_command="/speckit.plan",
        )

    stage = _infer_speckit_stage(iteration_dir)
    if stage == "implement":
        last_command = "/speckit-implement"
        next_command = "/speckit-implement"
    elif stage == "tasks":
        last_command = "/speckit.tasks"
        next_command = "/speckit-implement"
    elif stage == "plan":
        last_command = "/speckit.plan"
        next_command = "/speckit.tasks"
    elif stage == "spec":
        last_command = "/speckit.specify"
        next_command = "/speckit.plan"
    else:
        last_command = "/speckit.init"
        next_command = "/speckit.plan"

    return WorkflowStatus(
        workflow_type="speckit",
        current_iteration=iteration_dir.name,
        last_command=last_command,
        next_command=next_command,
    )


def _latest_speckit_iteration(root: Path) -> Path | None:
    roots = [r for r in (root / ".specify", root / "speckit", root / ".speckit") if r.is_dir()]
    candidates: list[Path] = []

    for marker_root in roots:
        iterations_dir = marker_root / "iterations"
        if iterations_dir.is_dir():
            candidates.extend(d for d in iterations_dir.iterdir() if d.is_dir())
        candidates.extend(d for d in marker_root.iterdir() if d.is_dir() and d.name.startswith("iteration-"))

    specs_root = root / "specs"
    if specs_root.is_dir():
        candidates.extend(d for d in specs_root.iterdir() if d.is_dir())

    if not candidates:
        return None
    return max(candidates, key=lambda d: d.stat().st_mtime)


def _infer_speckit_stage(iteration_dir: Path) -> str:
    # Use common artifact names in priority order from later to earlier phases.
    task_progress = _task_progress(iteration_dir / "tasks.md")
    if task_progress is not None and task_progress[1] > 0:
        return "implement"
    if _has_any_file(iteration_dir, "tasks.md", "todo.md"):
        return "tasks"
    if _has_any_file(iteration_dir, "plan.md"):
        return "plan"
    specs_dir = iteration_dir / "specs"
    if specs_dir.is_dir() and any(specs_dir.glob("**/*.md")):
        return "spec"
    if _has_any_file(iteration_dir, "spec.md", "specification.md"):
        return "spec"
    return "init"


def _has_any_file(directory: Path, *names: str) -> bool:
    return any((directory / name).is_file() for name in names)


def _task_progress(tasks_file: Path) -> tuple[int, int] | None:
    if not tasks_file.is_file():
        return None

    total = 0
    complete = 0
    for line in tasks_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ] "):
            total += 1
        elif stripped.startswith("- [x] "):
            total += 1
            complete += 1
    return total, complete

