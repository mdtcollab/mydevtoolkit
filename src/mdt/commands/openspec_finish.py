"""openspec_finish command: finish a change branch by merging it back into main."""
from __future__ import annotations

import subprocess
from pathlib import Path

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult

KNOWN_PREFIXES = {"feature", "bugfix", "hotfix", "chore", "refactor"}
DEFAULT_TARGET = "main"


def _get_current_branch(project_root: str) -> str | None:
    """Return the current git branch name, or None on failure."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _extract_change_name(branch: str) -> str | None:
    """Extract the change name from a branch, stripping known prefixes.

    Returns None if the branch doesn't have a recognised prefix.
    """
    parts = branch.split("/", 1)
    if len(parts) == 2 and parts[0] in KNOWN_PREFIXES:
        return parts[1]
    return None


def _is_working_tree_clean(project_root: str) -> bool:
    """Return True if the git working tree has no uncommitted changes."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == ""


def _change_folder_exists(project_root: str, change_name: str) -> bool:
    """Return True if the OpenSpec change folder still exists."""
    return (Path(project_root) / "openspec" / "changes" / change_name).is_dir()


def run_openspec_finish(project_root: str) -> CommandResult:
    """Execute the finish-change workflow."""
    target = DEFAULT_TARGET

    # 1. Detect current branch
    branch = _get_current_branch(project_root)
    if branch is None:
        return CommandResult(success=False, error="Could not determine the current git branch.")

    # 2. Extract change name
    change_name = _extract_change_name(branch)
    if change_name is None:
        return CommandResult(
            success=False,
            error=f"Branch '{branch}' is not an OpenSpec change branch. "
            f"Expected format: <prefix>/<change-name> (e.g. feature/my-change).",
        )

    # 3. Check if change folder still exists (must be archived first)
    if _change_folder_exists(project_root, change_name):
        return CommandResult(
            success=False,
            error=f"OpenSpec change folder 'openspec/changes/{change_name}/' still exists. "
            "Please archive the change first with /opsx:archive before finishing.",
        )

    # 4. Clean working tree
    if not _is_working_tree_clean(project_root):
        return CommandResult(
            success=False,
            error="Working tree has uncommitted changes. Please commit or stash them first.",
        )

    # 5. Switch to target branch
    checkout = subprocess.run(
        ["git", "checkout", target],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if checkout.returncode != 0:
        return CommandResult(
            success=False,
            error=f"Failed to switch to target branch '{target}': {checkout.stderr.strip()}",
        )

    # 6. Pull latest (best-effort)
    pull_warning = ""
    pull = subprocess.run(
        ["git", "pull"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if pull.returncode != 0:
        pull_warning = f" (warning: git pull failed — using local state: {pull.stderr.strip()})"

    # 7. Merge
    merge = subprocess.run(
        ["git", "merge", "--no-ff", branch],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if merge.returncode != 0:
        # Abort the failed merge to leave the repo in a clean state
        subprocess.run(
            ["git", "merge", "--abort"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        return CommandResult(
            success=False,
            error=f"Merge conflict merging '{branch}' into '{target}'. "
            "The merge has been aborted. Resolve conflicts manually and retry.",
        )

    return CommandResult(
        success=True,
        output=f"Merged '{branch}' into '{target}'.{pull_warning}",
        data={"source_branch": branch, "target_branch": target},
    )


class OpenspecFinishCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        root = str(context.repo_root or context.cwd)
        return run_openspec_finish(root)

