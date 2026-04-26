"""Workflow event history storage and lookup."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping

TrackedWorkflowType = Literal["openspec", "speckit"]

DEFAULT_EVENT_SOURCE = "unknown"
_HISTORY_FILENAME = "workflow-history.jsonl"


@dataclass(slots=True)
class WorkflowEvent:
    workflow_type: TrackedWorkflowType
    command_id: str
    raw_command: str
    timestamp: str
    success: bool
    project_path: str
    source: str = DEFAULT_EVENT_SOURCE
    change_name: str | None = None
    iteration_name: str | None = None

    @classmethod
    def from_payload(
        cls,
        payload: Mapping[str, Any],
        *,
        project_root: Path,
    ) -> "WorkflowEvent":
        workflow_type = _normalize_workflow_type(payload.get("workflow_type"))
        command_id = _require_non_empty_text(payload.get("command_id"), field_name="command_id")
        raw_command = _require_non_empty_text(payload.get("raw_command"), field_name="raw_command")
        success = _normalize_bool(payload.get("success"), field_name="success")
        timestamp = _normalize_timestamp(payload.get("timestamp"))
        source = _normalize_optional_text(payload.get("source")) or DEFAULT_EVENT_SOURCE
        change_name = _normalize_optional_text(payload.get("change_name"))
        iteration_name = _normalize_optional_text(payload.get("iteration_name"))

        if workflow_type == "openspec" and iteration_name is not None:
            raise ValueError("OpenSpec events cannot include iteration_name")
        if workflow_type == "speckit" and change_name is not None:
            raise ValueError("Spec Kit events cannot include change_name")

        return cls(
            workflow_type=workflow_type,
            command_id=command_id,
            raw_command=raw_command,
            timestamp=timestamp,
            success=success,
            project_path=str(project_root.resolve()),
            source=source,
            change_name=change_name,
            iteration_name=iteration_name,
        )

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "WorkflowEvent":
        return cls(
            workflow_type=_normalize_workflow_type(record.get("workflow_type")),
            command_id=_require_non_empty_text(record.get("command_id"), field_name="command_id"),
            raw_command=_require_non_empty_text(record.get("raw_command"), field_name="raw_command"),
            timestamp=_normalize_timestamp(record.get("timestamp")),
            success=_normalize_bool(record.get("success"), field_name="success"),
            project_path=_require_non_empty_text(record.get("project_path"), field_name="project_path"),
            source=_normalize_optional_text(record.get("source")) or DEFAULT_EVENT_SOURCE,
            change_name=_normalize_optional_text(record.get("change_name")),
            iteration_name=_normalize_optional_text(record.get("iteration_name")),
        )

    def to_record(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def last_command(self) -> str:
        return self.raw_command or self.command_id


class WorkflowHistoryStore:
    """Append-only project-local workflow event history."""

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root.resolve()
        self._history_path = self._project_root / ".mdt" / _HISTORY_FILENAME

    @property
    def history_path(self) -> Path:
        return self._history_path

    def append(self, event: WorkflowEvent) -> None:
        if event.project_path != str(self._project_root):
            raise ValueError("Workflow event project_path does not match the target project root")
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        with self._history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_record(), sort_keys=True))
            f.write("\n")

    def list_events(self) -> list[WorkflowEvent]:
        if not self._history_path.is_file():
            return []

        events: list[WorkflowEvent] = []
        for line in self._history_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
                events.append(WorkflowEvent.from_record(record))
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        return events

    def latest_successful_event(
        self,
        *,
        workflow_type: TrackedWorkflowType,
        change_name: str | None = None,
        iteration_name: str | None = None,
    ) -> WorkflowEvent | None:
        events = self.list_events()
        wildcard_candidate: WorkflowEvent | None = None

        for event in reversed(events):
            if event.workflow_type != workflow_type or not event.success:
                continue
            if event.project_path != str(self._project_root):
                continue

            if workflow_type == "openspec":
                if change_name:
                    if event.change_name == change_name:
                        return event
                    if event.change_name is None and wildcard_candidate is None:
                        wildcard_candidate = event
                    continue
                return event

            if iteration_name:
                if event.iteration_name == iteration_name:
                    return event
                if event.iteration_name is None and wildcard_candidate is None:
                    wildcard_candidate = event
                continue
            return event

        return wildcard_candidate


def record_workflow_event(project_root: Path, payload: Mapping[str, Any]) -> WorkflowEvent:
    event = WorkflowEvent.from_payload(payload, project_root=project_root)
    WorkflowHistoryStore(project_root).append(event)
    return event


def tracked_last_command_source(event: WorkflowEvent | None) -> str:
    if event is None:
        return "unknown"
    source = event.source.strip().lower()
    if source.startswith("tracked-"):
        return source
    return f"tracked-{source}"


def _normalize_workflow_type(value: Any) -> TrackedWorkflowType:
    text = _require_non_empty_text(value, field_name="workflow_type").lower()
    if text not in {"openspec", "speckit"}:
        raise ValueError("workflow_type must be 'openspec' or 'speckit'")
    return text


def _require_non_empty_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Optional text fields must be strings when provided")
    stripped = value.strip()
    return stripped or None


def _normalize_bool(value: Any, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    raise ValueError(f"{field_name} must be a boolean")


def _normalize_timestamp(value: Any) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty string when provided")
    text = value.strip()
    candidate = text.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError("timestamp must be a valid ISO-8601 string") from exc
    return text

