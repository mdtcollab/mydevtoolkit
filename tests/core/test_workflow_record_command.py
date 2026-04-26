from __future__ import annotations

from pathlib import Path

import pytest

from mdt.commands import build_command_registry
from mdt.commands.workflow_record import WorkflowRecordCommand
from mdt.core.context import ProjectContext
from mdt.core.dispatcher import CommandDispatcher
from mdt.core.registry import CommandRegistry
from mdt.workflow_event_cli import run


def _context(root: Path) -> ProjectContext:
    return ProjectContext(cwd=root, repo_root=root, project_name=None)


def test_workflow_record_command_records_valid_payload(tmp_path: Path) -> None:
    command = WorkflowRecordCommand(CommandRegistry())

    result = command(
        args=[
            "workflow_type=openspec",
            "command_id=apply",
            "raw_command=/opsx:apply",
            "success=true",
            "change_name=demo-change",
            "source=agent-hook",
        ],
        context=_context(tmp_path),
    )

    assert result.success is True
    assert result.data["workflow_type"] == "openspec"
    assert result.data["source"] == "agent-hook"
    assert (tmp_path / ".mdt" / "workflow-history.jsonl").is_file()


def test_workflow_record_command_rejects_invalid_payload(tmp_path: Path) -> None:
    command = WorkflowRecordCommand(CommandRegistry())

    result = command(
        args=["workflow_type=openspec", "command_id=apply"],
        context=_context(tmp_path),
    )

    assert result.success is False
    assert "raw_command is required" in (result.error or "")


def test_workflow_record_command_dispatches_as_two_word_command(tmp_path: Path) -> None:
    registry = build_command_registry()
    dispatcher = CommandDispatcher(registry, _context(tmp_path))

    result = dispatcher.dispatch(
        "workflow record workflow_type=speckit command_id=plan raw_command=/speckit.plan success=true source=agent-hook"
    )

    assert result.success is True
    assert result.data["workflow_type"] == "speckit"
    assert result.data["source"] == "agent-hook"


def test_workflow_record_cli_records_event(tmp_path: Path) -> None:
    exit_code = run(
        [
            "--project-root",
            str(tmp_path),
            "--workflow-type",
            "speckit",
            "--command-id",
            "implement",
            "--raw-command",
            "/speckit-implement",
            "--success",
            "true",
            "--iteration-name",
            "iteration-7",
            "--source",
            "agent-hook",
        ]
    )

    assert exit_code == 0
    history = (tmp_path / ".mdt" / "workflow-history.jsonl").read_text(encoding="utf-8")
    assert "/speckit-implement" in history
    assert "agent-hook" in history


def test_workflow_record_cli_rejects_conflicting_context(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        run(
            [
                "--project-root",
                str(tmp_path),
                "--workflow-type",
                "speckit",
                "--command-id",
                "plan",
                "--raw-command",
                "/speckit.plan",
                "--success",
                "true",
                "--change-name",
                "bad-change",
            ]
        )

