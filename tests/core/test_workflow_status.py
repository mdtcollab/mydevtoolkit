from __future__ import annotations

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
    assert status.next_command == "/opsx:archive"


def test_detects_speckit_only_and_infers_plan_to_tasks(tmp_path) -> None:
    iteration = tmp_path / "speckit" / "iterations" / "iteration-2"
    iteration.mkdir(parents=True)
    (iteration / "plan.md").write_text("plan\n", encoding="utf-8")

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "speckit"
    assert status.current_iteration == "iteration-2"
    assert status.last_command == "/speckit.plan"
    assert status.next_command == "/speckit.tasks"


def test_detects_speckit_iteration_without_artifacts_as_init(tmp_path) -> None:
    iteration = tmp_path / ".speckit" / "iterations" / "iteration-1"
    iteration.mkdir(parents=True)

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "speckit"
    assert status.current_iteration == "iteration-1"
    assert status.last_command == "/speckit.init"
    assert status.next_command == "/speckit.plan"


def test_detects_both_workflows_explicitly(tmp_path) -> None:
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    (tmp_path / "openspec" / "config.yaml").write_text("name: demo\n", encoding="utf-8")
    (tmp_path / "speckit" / "iterations" / "iteration-1").mkdir(parents=True)

    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "both"


def test_detects_no_supported_workflow(tmp_path) -> None:
    status = detect_workflow_status(tmp_path)

    assert status.workflow_type == "none"

