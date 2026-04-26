from __future__ import annotations

from mdt.core.workflow_history import record_workflow_event
from mdt.core.workflow_status import detect_workflow_status


def test_detects_openspec_only_and_recommends_apply(tmp_path) -> None:
    change = tmp_path / "openspec" / "changes" / "add-intellisense-support"
    change.mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (change / "proposal.md").write_text("ok\n", encoding="utf-8")
    (change / "design.md").write_text("ok\n", encoding="utf-8")
    (change / "specs" / "workflow" / "spec.md").parent.mkdir(parents=True)
    (change / "specs" / "workflow" / "spec.md").write_text("ok\n", encoding="utf-8")
    (change / "tasks.md").write_text("- [ ] 1.1 task\n", encoding="utf-8")

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "openspec"
    assert status.current_change == "add-intellisense-support"
    assert status.last_command == "/opsx:propose"
    assert status.last_command_source == "inferred"
    assert status.next_command == "/opsx:apply"


def test_openspec_apply_in_progress_recommends_continue_apply(tmp_path) -> None:
    change = tmp_path / "openspec" / "changes" / "ship-feature"
    change.mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (change / "proposal.md").write_text("ok\n", encoding="utf-8")
    (change / "design.md").write_text("ok\n", encoding="utf-8")
    (change / "specs" / "cap" / "spec.md").parent.mkdir(parents=True)
    (change / "specs" / "cap" / "spec.md").write_text("ok\n", encoding="utf-8")
    (change / "tasks.md").write_text("- [x] 1.1 done\n- [ ] 1.2 todo\n", encoding="utf-8")

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "openspec"
    assert status.last_command == "/opsx:apply"
    assert status.last_command_source == "inferred"
    assert status.next_command == "/opsx:apply"


def test_openspec_apply_complete_recommends_archive(tmp_path) -> None:
    change = tmp_path / "openspec" / "changes" / "done-change"
    change.mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (change / "tasks.md").write_text("- [x] 1.1 done\n", encoding="utf-8")

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "openspec"
    assert status.current_change == "done-change"
    assert status.last_command == "/opsx:apply"
    assert status.last_command_source == "inferred"
    assert status.next_command == "/opsx:archive"


def test_tracked_openspec_history_overrides_inferred_last_command(tmp_path) -> None:
    change = tmp_path / "openspec" / "changes" / "tracked-change"
    change.mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (change / "proposal.md").write_text("ok\n", encoding="utf-8")
    (change / "design.md").write_text("ok\n", encoding="utf-8")
    (change / "specs" / "cap" / "spec.md").parent.mkdir(parents=True)
    (change / "specs" / "cap" / "spec.md").write_text("ok\n", encoding="utf-8")
    (change / "tasks.md").write_text("- [ ] 1.1 todo\n", encoding="utf-8")
    record_workflow_event(
        tmp_path,
        {
            "workflow_type": "openspec",
            "command_id": "apply",
            "raw_command": "/opsx:apply",
            "success": True,
            "change_name": "tracked-change",
            "source": "agent-hook",
        },
    )

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "openspec"
    assert status.current_change == "tracked-change"
    assert status.last_command == "/opsx:apply"
    assert status.last_command_source == "tracked-agent-hook"
    assert status.next_command == "/opsx:apply"


def test_detects_speckit_only_and_infers_plan_to_tasks(tmp_path) -> None:
    iteration = tmp_path / ".specify" / "iterations" / "iteration-2"
    iteration.mkdir(parents=True)
    (iteration / "plan.md").write_text("plan\n", encoding="utf-8")

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "speckit"
    assert status.current_iteration == "iteration-2"
    assert status.last_command == "/speckit.plan"
    assert status.last_command_source == "inferred"
    assert status.next_command == "/speckit.tasks"


def test_detects_speckit_iteration_without_artifacts_as_init(tmp_path) -> None:
    iteration = tmp_path / ".speckit" / "iterations" / "iteration-1"
    iteration.mkdir(parents=True)

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "speckit"
    assert status.current_iteration == "iteration-1"
    assert status.last_command == "/speckit.init"
    assert status.last_command_source == "inferred"
    assert status.next_command == "/speckit.plan"


def test_detects_speckit_iteration_from_specs_folder(tmp_path) -> None:
    (tmp_path / ".specify").mkdir(parents=True)
    iteration = tmp_path / "specs" / "iteration-3"
    iteration.mkdir(parents=True)
    (iteration / "plan.md").write_text("plan\n", encoding="utf-8")

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "speckit"
    assert status.current_iteration == "iteration-3"
    assert status.last_command == "/speckit.plan"
    assert status.last_command_source == "inferred"
    assert status.next_command == "/speckit.tasks"


def test_detects_speckit_implement_when_tasks_have_started(tmp_path) -> None:
    iteration = tmp_path / ".specify" / "iterations" / "iteration-4"
    iteration.mkdir(parents=True)
    (iteration / "tasks.md").write_text("- [x] 1.1 started\n- [ ] 1.2 next\n", encoding="utf-8")

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "speckit"
    assert status.current_iteration == "iteration-4"
    assert status.last_command == "/speckit-implement"
    assert status.last_command_source == "inferred"
    assert status.next_command == "/speckit-implement"


def test_tracked_speckit_history_overrides_inferred_last_command(tmp_path) -> None:
    iteration = tmp_path / ".specify" / "iterations" / "iteration-8"
    iteration.mkdir(parents=True)
    (iteration / "plan.md").write_text("plan\n", encoding="utf-8")
    record_workflow_event(
        tmp_path,
        {
            "workflow_type": "speckit",
            "command_id": "implement",
            "raw_command": "/speckit-implement",
            "success": True,
            "iteration_name": "iteration-8",
            "source": "agent-hook",
        },
    )

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "speckit"
    assert status.current_iteration == "iteration-8"
    assert status.last_command == "/speckit-implement"
    assert status.last_command_source == "tracked-agent-hook"
    assert status.next_command == "/speckit.tasks"


def test_failed_newer_tracked_event_does_not_override_last_successful(tmp_path) -> None:
    iteration = tmp_path / ".specify" / "iterations" / "iteration-9"
    iteration.mkdir(parents=True)
    (iteration / "plan.md").write_text("plan\n", encoding="utf-8")
    record_workflow_event(
        tmp_path,
        {
            "workflow_type": "speckit",
            "command_id": "plan",
            "raw_command": "/speckit.plan",
            "success": True,
            "iteration_name": "iteration-9",
            "timestamp": "2026-04-26T09:00:00+00:00",
            "source": "agent-hook",
        },
    )
    record_workflow_event(
        tmp_path,
        {
            "workflow_type": "speckit",
            "command_id": "tasks",
            "raw_command": "/speckit.tasks",
            "success": False,
            "iteration_name": "iteration-9",
            "timestamp": "2026-04-26T10:00:00+00:00",
            "source": "agent-hook",
        },
    )

    status = detect_workflow_status(tmp_path)

    assert status.last_command == "/speckit.plan"
    assert status.last_command_source == "tracked-agent-hook"


def test_detects_both_workflows_explicitly(tmp_path) -> None:
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (tmp_path / ".specify" / "iterations" / "iteration-1").mkdir(parents=True)

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "both"


def test_detects_no_supported_workflow(tmp_path) -> None:
    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "none"

