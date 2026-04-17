"""Tests for settings_theme_set command."""
import pytest

from mdt.commands.settings_theme_set import SettingsThemeSetCommand
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.themes import get_active_theme, reset_active_theme


@pytest.fixture(autouse=True)
def _reset():
    reset_active_theme()
    yield
    reset_active_theme()


@pytest.fixture()
def command():
    registry = CommandRegistry()
    return SettingsThemeSetCommand(registry)


@pytest.fixture()
def context(tmp_path):
    return ProjectContext(cwd=tmp_path, repo_root=tmp_path, project_name="test")


class TestListThemes:
    def test_no_args_lists_themes(self, command, context):
        result = command(args=[], context=context)
        assert result.success is True
        assert "golden" in result.output
        assert "coral" in result.output


class TestSetTheme:
    def test_set_valid_theme(self, command, context):
        result = command(args=["coral"], context=context)
        assert result.success is True
        assert result.data["theme"] == "coral"
        assert get_active_theme().name == "coral"

    def test_set_unknown_theme(self, command, context):
        result = command(args=["nonexistent"], context=context)
        assert result.success is False
        assert "nonexistent" in result.error
        assert "golden" in result.error  # lists valid names

