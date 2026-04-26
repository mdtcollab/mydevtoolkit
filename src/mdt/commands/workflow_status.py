"""workflow_status command: inspect workflow state for OpenSpec or Spec Kit."""

from __future__ import annotations

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult
from mdt.core.workflow_status import WorkflowStatus, detect_workflow_status


class WorkflowStatusCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args
        root = context.repo_root or context.cwd
        status = detect_workflow_status(root)

        if status.workflow_type == "none":
            return CommandResult(
                success=False,
                error=(
                    "No supported workflow system found. "
                    "Expected OpenSpec markers under 'openspec/' or Spec Kit markers under "
                    "'.specify/', 'speckit/', or '.speckit/'."
                ),
                data={"workflow_type": "none"},
            )

        if status.workflow_type == "both":
            return CommandResult(
                success=False,
                error=(
                    "Both OpenSpec and Spec Kit markers were detected in this project. "
                    "Please keep only one workflow system active before running workflow status."
                ),
                data={"workflow_type": "both"},
            )

        lines = [f"workflow type: {status.workflow_type}"]
        if status.current_change:
            lines.append(f"current change: {status.current_change}")
        if status.current_iteration:
            lines.append(f"current iteration: {status.current_iteration}")
        if status.last_command:
            lines.append(f"last command: {status.last_command}")
        if status.next_command:
            lines.append(f"next recommended command: {status.next_command}")

        return CommandResult(
            success=True,
            output="\n".join(lines),
            data=_to_data(status),
        )


def _to_data(status: WorkflowStatus) -> dict[str, str]:
    data: dict[str, str] = {"workflow_type": status.workflow_type}
    if status.current_change:
        data["current_change"] = status.current_change
    if status.current_iteration:
        data["current_iteration"] = status.current_iteration
    if status.last_command:
        data["last_command"] = status.last_command
    if status.next_command:
        data["next_command"] = status.next_command
    return data

