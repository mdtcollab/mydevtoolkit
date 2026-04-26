from __future__ import annotations

from pathlib import Path

import pytest

from mdt.core.workflow_history import WorkflowEvent, WorkflowHistoryStore, record_workflow_event


def test_workflow_event_from_payload_normalizes_fields(tmp_path: Path) -> None:
    event = WorkflowEvent.from_payload(
        {
            "workflow_type": "openspec",
            "command_id": "apply",
            "raw_command": "/opsx:apply",
            "success": "true",
            "change_name": "demo-change",
            "source": "agent-hook",
        },
        project_root=tmp_path,
    )

    assert event.workflow_type == "openspec"
    assert event.command_id == "apply"
    assert event.raw_command == "/opsx:apply"
    assert event.success is True
    assert event.change_name == "demo-change"
    assert event.source == "agent-hook"
    assert event.project_path == str(tmp_path.resolve())
    assert event.timestamp


def test_workflow_event_requires_mandatory_fields(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        WorkflowEvent.from_payload(
            {
                "workflow_type": "openspec",
                "command_id": "apply",
                "success": True,
            },
            project_root=tmp_path,
        )


def test_record_and_load_workflow_event_persists_history(tmp_path: Path) -> None:
    event = record_workflow_event(
        tmp_path,
        {
            "workflow_type": "speckit",
            "command_id": "plan",
            "raw_command": "/speckit.plan",
            "success": True,
            "iteration_name": "iteration-2",
            "source": "agent-hook",
        },
    )

    store = WorkflowHistoryStore(tmp_path)
    loaded = store.list_events()

    assert event.project_path == str(tmp_path.resolve())
    assert store.history_path == tmp_path / ".mdt" / "workflow-history.jsonl"
    assert len(loaded) == 1
    assert loaded[0].last_command == "/speckit.plan"
    assert loaded[0].iteration_name == "iteration-2"


def test_latest_successful_event_prefers_matching_context_and_skips_failures(tmp_path: Path) -> None:
    store = WorkflowHistoryStore(tmp_path)
    store.append(
        WorkflowEvent.from_payload(
            {
                "workflow_type": "openspec",
                "command_id": "propose",
                "raw_command": "/opsx:propose",
                "success": True,
                "change_name": "old-change",
                "timestamp": "2026-04-26T10:00:00+00:00",
                "source": "agent-hook",
            },
            project_root=tmp_path,
        )
    )
    store.append(
        WorkflowEvent.from_payload(
            {
                "workflow_type": "openspec",
                "command_id": "apply",
                "raw_command": "/opsx:apply",
                "success": True,
                "change_name": "target-change",
                "timestamp": "2026-04-26T11:00:00+00:00",
                "source": "agent-hook",
            },
            project_root=tmp_path,
        )
    )
    store.append(
        WorkflowEvent.from_payload(
            {
                "workflow_type": "openspec",
                "command_id": "archive",
                "raw_command": "/opsx:archive",
                "success": False,
                "change_name": "target-change",
                "timestamp": "2026-04-26T12:00:00+00:00",
                "source": "agent-hook",
            },
            project_root=tmp_path,
        )
    )

    event = store.latest_successful_event(
        workflow_type="openspec",
        change_name="target-change",
    )

    assert event is not None
    assert event.last_command == "/opsx:apply"


def test_latest_successful_event_uses_contextless_event_as_fallback(tmp_path: Path) -> None:
    record_workflow_event(
        tmp_path,
        {
            "workflow_type": "speckit",
            "command_id": "plan",
            "raw_command": "/speckit.plan",
            "success": True,
            "source": "agent-hook",
        },
    )

    event = WorkflowHistoryStore(tmp_path).latest_successful_event(
        workflow_type="speckit",
        iteration_name="iteration-9",
    )

    assert event is not None
    assert event.last_command == "/speckit.plan"

