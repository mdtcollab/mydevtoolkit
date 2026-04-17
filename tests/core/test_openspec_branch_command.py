"""Tests for OpenspecBranchCommand."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mdt.commands.openspec_branch import (
    OpenspecBranchCommand,
    _build_branch_name,
    _latest_change_name,
    run_openspec_branch,
)
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry


def make_context(root: str) -> ProjectContext:
    return ProjectContext(cwd=Path(root), repo_root=Path(root), project_name=None)


class TestLatestChangeName:
    def test_returns_none_when_no_changes_dir(self, tmp_path):
        assert _latest_change_name(str(tmp_path)) is None

    def test_returns_none_when_empty_changes_dir(self, tmp_path):
        (tmp_path / "openspec" / "changes").mkdir(parents=True)
        assert _latest_change_name(str(tmp_path)) is None

    def test_returns_most_recently_modified(self, tmp_path):
        changes = tmp_path / "openspec" / "changes"
        changes.mkdir(parents=True)
        old = changes / "old-change"
        old.mkdir()
        new = changes / "new-change"
        new.mkdir()
        # ensure different mtime
        os.utime(old, (0, 0))
        assert _latest_change_name(str(tmp_path)) == "new-change"


class TestBuildBranchName:
    def test_adds_feature_prefix_when_none(self):
        assert _build_branch_name("my-change") == "feature/my-change"

    def test_keeps_existing_prefix(self):
        assert _build_branch_name("bugfix/my-fix") == "bugfix/my-fix"


class TestRunOpenspecBranch:
    def test_error_when_no_changes(self, tmp_path):
        result = run_openspec_branch(str(tmp_path))
        assert not result.success
        assert "No OpenSpec changes" in result.error

    def test_creates_branch_on_success(self, tmp_path):
        changes = tmp_path / "openspec" / "changes" / "my-feature"
        changes.mkdir(parents=True)

        mock_result = MagicMock(returncode=0, stderr="")
        with patch("mdt.commands.openspec_branch.subprocess.run", return_value=mock_result) as mock_run:
            result = run_openspec_branch(str(tmp_path))

        assert result.success
        assert "feature/my-feature" in result.output
        mock_run.assert_called_once_with(
            ["git", "checkout", "-b", "feature/my-feature"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
        )

    def test_error_on_git_failure(self, tmp_path):
        changes = tmp_path / "openspec" / "changes" / "my-feature"
        changes.mkdir(parents=True)

        mock_result = MagicMock(returncode=1, stderr="fatal: branch already exists")
        with patch("mdt.commands.openspec_branch.subprocess.run", return_value=mock_result):
            result = run_openspec_branch(str(tmp_path))

        assert not result.success
        assert "fatal" in result.error


class TestOpenspecBranchCommand:
    def test_delegates_to_run(self, tmp_path):
        registry = CommandRegistry()
        cmd = OpenspecBranchCommand(registry)
        context = make_context(str(tmp_path))
        with patch("mdt.commands.openspec_branch.run_openspec_branch") as mock_run:
            mock_run.return_value = MagicMock(success=True)
            cmd(args=[], context=context)
            mock_run.assert_called_once_with(str(tmp_path))


