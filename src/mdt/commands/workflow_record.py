"""workflow_record command: record a workflow event for external integrations."""

from __future__ import annotations

from typing import Any

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult
from mdt.core.workflow_history import WorkflowEvent, record_workflow_event


class WorkflowRecordCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        try:
            payload = parse_workflow_event_args(args)
            root = context.repo_root or context.cwd
            event = record_workflow_event(root, payload)
        except ValueError as exc:
            return CommandResult(success=False, error=str(exc))

        return CommandResult(
            success=True,
            output=f"Recorded workflow event: {event.last_command}",
            data=_event_to_data(event),
        )


def parse_workflow_event_args(args: list[str]) -> dict[str, Any]:
    if not args:
        raise ValueError(
            "Usage: workflow record workflow_type=<openspec|speckit> command_id=<id> "
            "raw_command=<command> success=<true|false> [source=<source>] "
            "[change_name=<name>] [iteration_name=<name>] [timestamp=<iso8601>]"
        )

    payload: dict[str, Any] = {}
    for arg in args:
        if "=" not in arg:
            raise ValueError(f"Invalid workflow event argument '{arg}'. Expected key=value.")
        key, value = arg.split("=", 1)
        normalized_key = key.strip().lower()
        if not normalized_key:
            raise ValueError("Workflow event argument keys cannot be empty")
        payload[normalized_key] = value
    return payload


def _event_to_data(event: WorkflowEvent) -> dict[str, Any]:
    data: dict[str, Any] = {
        "workflow_type": event.workflow_type,
        "command_id": event.command_id,
        "raw_command": event.raw_command,
        "timestamp": event.timestamp,
        "success": event.success,
        "project_path": event.project_path,
        "source": event.source,
    }
    if event.change_name:
        data["change_name"] = event.change_name
    if event.iteration_name:
        data["iteration_name"] = event.iteration_name
    return data


