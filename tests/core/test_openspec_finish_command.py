"""Tests for OpenspecFinishCommand."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from mdt.commands.openspec_finish import (
    OpenspecFinishCommand,
    _extract_change_name,
    _get_current_branch,
    _is_working_tree_clean,
    _change_folder_exists,
    run_openspec_finish,
)
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry


def make_context(root: str) -> ProjectContext:
    return ProjectContext(cwd=Path(root), repo_root=Path(root), project_name=None)


class TestExtractChangeName:
    def test_feature_prefix(self):
        assert _extract_change_name("feature/my-change") == "my-change"

    def test_bugfix_prefix(self):
        assert _extract_change_name("bugfix/fix-thing") == "fix-thing"

    def test_hotfix_prefix(self):
        assert _extract_change_name("hotfix/urgent") == "urgent"

    def test_chore_prefix(self):
        assert _extract_change_name("chore/cleanup") == "cleanup"

    def test_refactor_prefix(self):
        assert _extract_change_name("refactor/restructure") == "restructure"

    def test_no_prefix_returns_none(self):
        assert _extract_change_name("main") is None

    def test_unknown_prefix_returns_none(self):
        assert _extract_change_name("release/v1") is None

    def test_nested_slashes_preserved(self):
        assert _extract_change_name("feature/some/nested") == "some/nested"


class TestGetCurrentBranch:
    def test_returns_branch_name(self, tmp_path):
        mock = MagicMock(returncode=0, stdout="feature/my-change\n")
        with patch("mdt.commands.openspec_finish.subprocess.run", return_value=mock):
            assert _get_current_branch(str(tmp_path)) == "feature/my-change"

    def test_returns_none_on_failure(self, tmp_path):
        mock = MagicMock(returncode=1, stdout="")
        with patch("mdt.commands.openspec_finish.subprocess.run", return_value=mock):
            assert _get_current_branch(str(tmp_path)) is None


class TestIsWorkingTreeClean:
    def test_clean(self, tmp_path):
        mock = MagicMock(returncode=0, stdout="")
        with patch("mdt.commands.openspec_finish.subprocess.run", return_value=mock):
            assert _is_working_tree_clean(str(tmp_path)) is True

    def test_dirty(self, tmp_path):
        mock = MagicMock(returncode=0, stdout=" M file.py\n")
        with patch("mdt.commands.openspec_finish.subprocess.run", return_value=mock):
            assert _is_working_tree_clean(str(tmp_path)) is False


class TestChangeFolderExists:
    def test_exists(self, tmp_path):
        (tmp_path / "openspec" / "changes" / "my-change").mkdir(parents=True)
        assert _change_folder_exists(str(tmp_path), "my-change") is True

    def test_not_exists(self, tmp_path):
        assert _change_folder_exists(str(tmp_path), "my-change") is False


class TestRunOpenspecFinish:
    def _mock_subprocess(self, side_effects):
        """Helper to mock sequential subprocess.run calls."""
        return patch(
            "mdt.commands.openspec_finish.subprocess.run",
            side_effect=side_effects,
        )

    def test_error_when_branch_unknown(self, tmp_path):
        mock = MagicMock(returncode=1, stdout="")
        with self._mock_subprocess([mock]):
            result = run_openspec_finish(str(tmp_path))
        assert not result.success
        assert "Could not determine" in result.error

    def test_error_when_not_change_branch(self, tmp_path):
        mock = MagicMock(returncode=0, stdout="main\n")
        with self._mock_subprocess([mock]):
            result = run_openspec_finish(str(tmp_path))
        assert not result.success
        assert "not an OpenSpec change branch" in result.error

    def test_error_when_change_folder_exists(self, tmp_path):
        (tmp_path / "openspec" / "changes" / "my-change").mkdir(parents=True)
        mock_branch = MagicMock(returncode=0, stdout="feature/my-change\n")
        with self._mock_subprocess([mock_branch]):
            result = run_openspec_finish(str(tmp_path))
        assert not result.success
        assert "opsx:archive" in result.error

    def test_error_when_dirty_tree(self, tmp_path):
        mock_branch = MagicMock(returncode=0, stdout="feature/my-change\n")
        mock_status = MagicMock(returncode=0, stdout=" M dirty.py\n")
        with self._mock_subprocess([mock_branch, mock_status]):
            result = run_openspec_finish(str(tmp_path))
        assert not result.success
        assert "uncommitted changes" in result.error

    def test_error_when_target_branch_missing(self, tmp_path):
        mock_branch = MagicMock(returncode=0, stdout="feature/my-change\n")
        mock_status = MagicMock(returncode=0, stdout="")
        mock_checkout = MagicMock(returncode=1, stderr="error: pathspec 'main' did not match")
        with self._mock_subprocess([mock_branch, mock_status, mock_checkout]):
            result = run_openspec_finish(str(tmp_path))
        assert not result.success
        assert "Failed to switch" in result.error

    def test_pull_failure_continues(self, tmp_path):
        mock_branch = MagicMock(returncode=0, stdout="feature/my-change\n")
        mock_status = MagicMock(returncode=0, stdout="")
        mock_checkout = MagicMock(returncode=0, stderr="")
        mock_pull = MagicMock(returncode=1, stderr="no remote configured")
        mock_merge = MagicMock(returncode=0, stdout="Merge made")
        with self._mock_subprocess([mock_branch, mock_status, mock_checkout, mock_pull, mock_merge]):
            result = run_openspec_finish(str(tmp_path))
        assert result.success
        assert "warning" in result.output

    def test_successful_merge(self, tmp_path):
        mock_branch = MagicMock(returncode=0, stdout="feature/my-change\n")
        mock_status = MagicMock(returncode=0, stdout="")
        mock_checkout = MagicMock(returncode=0, stderr="")
        mock_pull = MagicMock(returncode=0, stderr="")
        mock_merge = MagicMock(returncode=0, stdout="Merge made")
        with self._mock_subprocess([mock_branch, mock_status, mock_checkout, mock_pull, mock_merge]):
            result = run_openspec_finish(str(tmp_path))
        assert result.success
        assert "feature/my-change" in result.output
        assert "main" in result.output
        assert result.data["source_branch"] == "feature/my-change"
        assert result.data["target_branch"] == "main"

    def test_merge_conflict_aborts(self, tmp_path):
        mock_branch = MagicMock(returncode=0, stdout="feature/my-change\n")
        mock_status = MagicMock(returncode=0, stdout="")
        mock_checkout = MagicMock(returncode=0, stderr="")
        mock_pull = MagicMock(returncode=0, stderr="")
        mock_merge = MagicMock(returncode=1, stdout="CONFLICT")
        mock_abort = MagicMock(returncode=0)
        with self._mock_subprocess([mock_branch, mock_status, mock_checkout, mock_pull, mock_merge, mock_abort]):
            result = run_openspec_finish(str(tmp_path))
        assert not result.success
        assert "Merge conflict" in result.error
        assert "aborted" in result.error


class TestOpenspecFinishCommand:
    def test_delegates_to_run(self, tmp_path):
        registry = CommandRegistry()
        cmd = OpenspecFinishCommand(registry)
        context = make_context(str(tmp_path))
        with patch("mdt.commands.openspec_finish.run_openspec_finish") as mock_run:
            mock_run.return_value = MagicMock(success=True)
            cmd(args=[], context=context)
            mock_run.assert_called_once_with(str(tmp_path))

