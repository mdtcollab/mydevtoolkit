from __future__ import annotations

from pathlib import Path

from mdt.commands import build_command_registry
from mdt.commands.workflow_status import WorkflowStatusCommand
from mdt.core.context import ProjectContext
from mdt.core.dispatcher import CommandDispatcher
from mdt.core.registry import CommandRegistry


def _context(root: Path) -> ProjectContext:
    return ProjectContext(cwd=root, repo_root=root, project_name=None)


def test_command_outputs_openspec_fields(tmp_path) -> None:
    change = tmp_path / "openspec" / "changes" / "add-intellisense-support"
    change.mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (change / "proposal.md").write_text("ok\n", encoding="utf-8")
    (change / "design.md").write_text("ok\n", encoding="utf-8")
    (change / "specs" / "cap" / "spec.md").parent.mkdir(parents=True)
    (change / "specs" / "cap" / "spec.md").write_text("ok\n", encoding="utf-8")
    (change / "tasks.md").write_text("- [ ] 1.1 task\n", encoding="utf-8")

    command = WorkflowStatusCommand(CommandRegistry())
    result = command(args=[], context=_context(tmp_path))

    assert result.success is True
    assert "workflow type: openspec" in result.output
    assert "current change: add-intellisense-support" in result.output
    assert "last command: /opsx:propose" in result.output
    assert "next recommended command: /opsx:apply" in result.output


def test_command_returns_explicit_error_for_both(tmp_path) -> None:
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (tmp_path / "speckit" / "iterations" / "iteration-1").mkdir(parents=True)

    command = WorkflowStatusCommand(CommandRegistry())
    result = command(args=[], context=_context(tmp_path))

    assert result.success is False
    assert "Both OpenSpec and Spec Kit markers" in (result.error or "")
    assert result.data["workflow_type"] == "both"


def test_command_returns_explicit_error_for_none(tmp_path) -> None:
    command = WorkflowStatusCommand(CommandRegistry())
    result = command(args=[], context=_context(tmp_path))

    assert result.success is False
    assert "No supported workflow system found" in (result.error or "")
    assert result.data["workflow_type"] == "none"


def test_workflow_status_registered_for_two_word_dispatch(tmp_path) -> None:
    (tmp_path / "openspec" / "changes" / "demo-change").mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")

    registry = build_command_registry()
    dispatcher = CommandDispatcher(registry, _context(tmp_path))
    result = dispatcher.dispatch("workflow status")

    assert result.success is True
    assert "workflow type: openspec" in result.output


def test_workflow_category_is_discoverable_in_completions() -> None:
    registry = build_command_registry()

    assert "workflow" in registry.get_completions("w")
    assert "status" in registry.get_completions("workflow ")

