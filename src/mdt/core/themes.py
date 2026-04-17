"""Theme registry for the mdt interactive shell."""
from __future__ import annotations

from typing import NamedTuple


class Theme(NamedTuple):
    """A shell UI theme with five coordinated colors."""

    name: str
    primary: str
    secondary: str
    accent: str
    surface: str
    highlight: str


BUILTIN_THEMES: list[Theme] = [
    Theme(
        name="golden",
        primary="#F9DC5C",
        secondary="#FAE588",
        accent="#FCEFB4",
        surface="#FDF8E1",
        highlight="#F9DC5C",
    ),
    Theme(
        name="grape",
        primary="#EEEAFD",
        secondary="#D8CAF6",
        accent="#C2A9EF",
        surface="#AC88E8",
        highlight="#9667E0",
    ),
    Theme(
        name="clay",
        primary="#8C9579",
        secondary="#EACFA5",
        accent="#E6BB96",
        surface="#BE9A98",
        highlight="#AA7A79",
    ),
    Theme(
        name="candy",
        primary="#EFFFDF",
        secondary="#CEFFC4",
        accent="#B3F9FF",
        surface="#B9D4FF",
        highlight="#FFD1FF",
    ),
    Theme(
        name="teal",
        primary="#006767",
        secondary="#008080",
        accent="#279E9D",
        surface="#4EBCBA",
        highlight="#75DAD7",
    ),
    Theme(
        name="coral",
        primary="#EC5353",
        secondary="#EE7272",
        accent="#F09191",
        surface="#F2B0B0",
        highlight="#F3CFCE",
    ),
    Theme(
        name="dusk",
        primary="#4E6BA6",
        secondary="#938FB8",
        accent="#D8B5BE",
        surface="#398AA2",
        highlight="#1E7590",
    ),
    Theme(
        name="bubblegum",
        primary="#B7EDF7",
        secondary="#B4DAF9",
        accent="#FED8EC",
        surface="#FBB1D3",
        highlight="#FFF1C2",
    ),
    Theme(
        name="mist",
        primary="#FDE2E4",
        secondary="#F0EFEB",
        accent="#C5DEDD",
        surface="#BCD4E6",
        highlight="#99C1DE",
    ),
    Theme(
        name="rainbow",
        primary="#9BF6FF",
        secondary="#CAFFBF",
        accent="#FDFFB6",
        surface="#FFD6A5",
        highlight="#FFADAD",
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

