"""Tests for GitBranchCommand and branch name normalisation."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mdt.commands.git_branch import (
    GitBranchCommand,
    normalise_branch_name,
    run_git_branch,
)
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry


def make_context(root: str = "/fake") -> ProjectContext:
    return ProjectContext(cwd=Path(root), repo_root=Path(root), project_name=None)


class TestNormaliseBranchName:
    def test_valid_input(self):
        name, err = normalise_branch_name(["feature", "abc-123", "login", "system"])
        assert name == "feature/abc-123-login-system"
        assert err == ""

    def test_bugfix_category(self):
        name, _ = normalise_branch_name(["bugfix", "abc-456", "header", "styling"])
        assert name == "bugfix/abc-456-header-styling"

    def test_ticket_normalised_to_lowercase(self):
        name, _ = normalise_branch_name(["feature", "ABC-123", "login"])
        assert "abc-123" in name

    def test_missing_category_returns_error(self):
        name, err = normalise_branch_name(["abc-123", "login", "page"])
        assert name is None
        assert "category" in err.lower()

    def test_missing_ticket_returns_error(self):
        name, err = normalise_branch_name(["feature", "login", "page"])
        assert name is None
        assert "ticket" in err.lower()

    def test_missing_description_returns_error(self):
        name, err = normalise_branch_name(["feature", "abc-123"])
        assert name is None
        assert "description" in err.lower()

    def test_extra_punctuation_stripped(self):
        name, _ = normalise_branch_name(["feature", "abc-123", "new-login-page"])
        assert name == "feature/abc-123-new-login-page"


class TestRunGitBranch:
    def test_no_args_returns_error(self):
        result = run_git_branch([], "/fake")
        assert not result.success

    def test_creates_branch_on_success(self):
        mock_result = MagicMock(returncode=0, stderr="")
        with patch("mdt.commands.git_branch.subprocess.run", return_value=mock_result) as mock_run:
            result = run_git_branch(["feature", "abc-123", "login", "system"], "/fake")

        assert result.success
        assert "feature/abc-123-login-system" in result.output

    def test_git_failure_propagated(self):
        mock_result = MagicMock(returncode=1, stderr="fatal: branch exists")
        with patch("mdt.commands.git_branch.subprocess.run", return_value=mock_result):
            result = run_git_branch(["feature", "abc-123", "login"], "/fake")

        assert not result.success
        assert "fatal" in result.error


class TestGitBranchCommand:
    def test_delegates_to_run(self):
        registry = CommandRegistry()
        cmd = GitBranchCommand(registry)
        context = make_context()
        with patch("mdt.commands.git_branch.run_git_branch") as mock_run:
            mock_run.return_value = MagicMock(success=True)
            cmd(args=["feature", "abc-123", "test"], context=context)
            mock_run.assert_called_once_with(["feature", "abc-123", "test"], "/fake")


class TestGitBranchCommandCompletions:
    """Tests for GitBranchCommand.get_completions method."""

    def test_position_0_returns_all_prefixes_with_empty_input(self):
        result = GitBranchCommand.get_completions(0, [])
        assert result == ["bugfix", "chore", "feature", "hotfix", "refactor"]

    def test_position_0_filters_by_prefix(self):
        result = GitBranchCommand.get_completions(0, ["fe"])
        assert result == ["feature"]

    def test_position_0_filters_by_prefix_case_insensitive(self):
        result = GitBranchCommand.get_completions(0, ["FE"])
        assert result == ["feature"]

    def test_position_0_multiple_matches(self):
        result = GitBranchCommand.get_completions(0, ["b"])
        assert result == ["bugfix"]

    def test_position_0_partial_prefix_hotfix(self):
        result = GitBranchCommand.get_completions(0, ["ho"])
        assert result == ["hotfix"]

    def test_position_1_returns_empty_list(self):
        result = GitBranchCommand.get_completions(1, ["abc"])
        assert result == []

    def test_position_2_returns_empty_list(self):
        result = GitBranchCommand.get_completions(2, ["test"])
        assert result == []
