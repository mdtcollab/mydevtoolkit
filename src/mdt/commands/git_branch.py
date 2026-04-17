"""git_branch command: normalise free-text into a branch name and create it."""
from __future__ import annotations

import re
import subprocess

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult

KNOWN_PREFIXES = {"feature", "bugfix", "hotfix", "chore", "refactor"}
TICKET_RE = re.compile(r"^[a-z]+-[0-9]+$")


def normalise_branch_name(tokens: list[str]) -> tuple[str, str] | tuple[None, str]:
    """Return (branch_name, "") on success or (None, error_message) on failure."""
    lowered = [t.lower() for t in tokens]
    prefix: str | None = None
    ticket: str | None = None
    slug_parts: list[str] = []

    for tok in lowered:
        if prefix is None and tok in KNOWN_PREFIXES:
            prefix = tok
        elif ticket is None and TICKET_RE.match(tok):
            ticket = tok
        else:
            # strip non-alphanumeric separators and add as slug words
            word = re.sub(r"[^a-z0-9]+", "-", tok).strip("-")
            if word:
                slug_parts.append(word)

    if prefix is None:
        valid = ", ".join(sorted(KNOWN_PREFIXES))
        return None, f"Missing category prefix. Use one of: {valid}"
    if ticket is None:
        return None, "Missing ticket number. Expected format: abc-123 (lowercase letters, hyphen, digits)"
    if not slug_parts:
        return None, "Missing description. Provide a short description after the ticket number."

    branch_name = f"{prefix}/{ticket}-{'-'.join(slug_parts)}"
    return branch_name, ""


def run_git_branch(args: list[str], project_root: str) -> CommandResult:
    if not args:
        return CommandResult(
            success=False,
            error="Usage: git branch <category> <ticket> <description...>",
        )
    branch_name, err = normalise_branch_name(args)
    if branch_name is None:
        return CommandResult(success=False, error=err)

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


class GitBranchCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        root = str(context.repo_root or context.cwd)
        return run_git_branch(args, root)

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        """Return completion candidates for the given argument position.

        Position 0: category prefix (feature, bugfix, etc.)
        Other positions: no predefined completions
        """
        if position == 0:
            prefix = tokens[0].lower() if tokens else ""
            return sorted(p for p in KNOWN_PREFIXES if p.startswith(prefix))
        return []
