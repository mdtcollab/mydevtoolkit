"""Theme registry for the mdt interactive shell."""
from __future__ import annotations

from typing import NamedTuple


class Theme(NamedTuple):
    """A shell UI theme with four coordinated pastel colors."""

    name: str
    primary: str
    secondary: str
    accent: str
    surface: str


BUILTIN_THEMES: list[Theme] = [
    Theme(
        name="ocean",
        primary="#a0c4ff",
        secondary="#bdb2ff",
        accent="#caffbf",
        surface="#ffd6a5",
    ),
    Theme(
        name="sunset",
        primary="#ffadad",
        secondary="#ffd6a5",
        accent="#fdffb6",
        surface="#e4c1f9",
    ),
    Theme(
        name="forest",
        primary="#b7e4c7",
        secondary="#d5f5e3",
        accent="#fde2e4",
        surface="#d4a5a5",
    ),
    Theme(
        name="lavender",
        primary="#e4c1f9",
        secondary="#c8b6ff",
        accent="#bbd0ff",
        surface="#ffc8dd",
    ),
    Theme(
        name="peach",
        primary="#ffc8dd",
        secondary="#ffafcc",
        accent="#a2d2ff",
        surface="#cdb4db",
    ),
]


class ThemeRegistry:
    """Registry of available shell themes."""

    def __init__(self, themes: list[Theme] | None = None) -> None:
        self._themes = {t.name: t for t in (themes or BUILTIN_THEMES)}

    def list_themes(self) -> list[Theme]:
        return list(self._themes.values())

    def get_theme(self, name: str) -> Theme | None:
        return self._themes.get(name)


_registry = ThemeRegistry()
_active_theme_name: str = BUILTIN_THEMES[0].name


def get_active_theme() -> Theme:
    """Return the currently active theme."""
    theme = _registry.get_theme(_active_theme_name)
    assert theme is not None
    return theme


def set_active_theme(name: str) -> None:
    """Set the active theme by name. Raises ValueError if unknown."""
    global _active_theme_name  # noqa: PLW0603
    if _registry.get_theme(name) is None:
        valid = ", ".join(t.name for t in _registry.list_themes())
        raise ValueError(f"Unknown theme '{name}'. Available: {valid}")
    _active_theme_name = name


def reset_active_theme() -> None:
    """Reset to default theme (for testing)."""
    global _active_theme_name  # noqa: PLW0603
    _active_theme_name = BUILTIN_THEMES[0].name

