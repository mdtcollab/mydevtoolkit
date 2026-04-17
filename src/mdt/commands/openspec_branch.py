"""openspec_branch command: create a git branch named after the latest OpenSpec change."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult

KNOWN_PREFIXES = {"feature", "bugfix", "hotfix", "chore", "refactor"}


def _latest_change_name(project_root: str) -> str | None:
    changes_dir = Path(project_root) / "openspec" / "changes"
    if not changes_dir.is_dir():
        return None
    subdirs = [d for d in changes_dir.iterdir() if d.is_dir()]
    if not subdirs:
        return None
    return max(subdirs, key=lambda d: d.stat().st_mtime).name


def _build_branch_name(change_name: str) -> str:
    prefix = change_name.split("/")[0] if "/" in change_name else None
    if prefix in KNOWN_PREFIXES:
        return change_name
    return f"feature/{change_name}"


def run_openspec_branch(project_root: str) -> CommandResult:
    change_name = _latest_change_name(project_root)
    if not change_name:
        return CommandResult(
            success=False,
            error="No OpenSpec changes found in openspec/changes/",
        )
    branch_name = _build_branch_name(change_name)
    result = subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return CommandResult(success=False, error=result.stderr.strip())
    return CommandResult(
        success=True,
        output=f"Created and switched to branch: {branch_name}",
        data={"branch": branch_name},
    )


class OpenspecBranchCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        root = str(context.repo_root or context.cwd)
        return run_openspec_branch(root)


