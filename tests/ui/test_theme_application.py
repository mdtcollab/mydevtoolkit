"""Tests for theme application in ShellScreen."""
from mdt.core.themes import get_active_theme, reset_active_theme, set_active_theme


def test_theme_applies_after_set():
    """Verify set_active_theme changes what get_active_theme returns."""
    reset_active_theme()
    original = get_active_theme()
    set_active_theme("sunset")
    updated = get_active_theme()
    assert updated.name == "sunset"
    assert updated.name != original.name
    assert updated.primary != original.primary
    reset_active_theme()


def test_theme_colors_are_four_fields():
    """Each theme exposes exactly primary, secondary, accent, surface."""
    theme = get_active_theme()
    assert theme.primary
    assert theme.secondary
    assert theme.accent
    assert theme.surface

