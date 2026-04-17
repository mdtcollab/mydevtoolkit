"""Tests for mdt.core.themes module."""
import pytest

from mdt.core.themes import (
    BUILTIN_THEMES,
    Theme,
    ThemeRegistry,
    get_active_theme,
    reset_active_theme,
    set_active_theme,
)


@pytest.fixture(autouse=True)
def _reset_theme():
    reset_active_theme()
    yield
    reset_active_theme()


class TestThemeDataModel:
    def test_fields_accessible(self):
        t = Theme(name="golden", primary="#F9DC5C", secondary="#FAE588", accent="#FCEFB4", surface="#FDF8E1", highlight="#F9DC5C")
        assert t.name == "golden"
        assert t.primary == "#F9DC5C"
        assert t.secondary == "#FAE588"
        assert t.accent == "#FCEFB4"
        assert t.surface == "#FDF8E1"
        assert t.highlight == "#F9DC5C"


class TestThemeRegistry:
    def test_list_themes_returns_at_least_five(self):
        registry = ThemeRegistry()
        themes = registry.list_themes()
        assert len(themes) >= 5
        names = [t.name for t in themes]
        assert len(set(names)) == len(names)

    def test_get_theme_known(self):
        registry = ThemeRegistry()
        theme = registry.get_theme("golden")
        assert theme is not None
        assert theme.name == "golden"

    def test_get_theme_unknown(self):
        registry = ThemeRegistry()
        assert registry.get_theme("nonexistent") is None


class TestActiveTheme:
    def test_default_active_theme(self):
        theme = get_active_theme()
        assert theme.name == BUILTIN_THEMES[0].name

    def test_set_active_theme(self):
        set_active_theme("coral")
        assert get_active_theme().name == "coral"

    def test_set_unknown_theme_raises(self):
        with pytest.raises(ValueError, match="Unknown theme"):
            set_active_theme("nonexistent")

