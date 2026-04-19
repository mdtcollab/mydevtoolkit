"""Persistent settings for MDT stored at ~/.config/mdt/settings.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path.home() / ".config" / "mdt" / "settings.json"

_cache: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _cache  # noqa: PLW0603
    if _cache is not None:
        return _cache
    if SETTINGS_PATH.is_file():
        with open(SETTINGS_PATH) as f:
            _cache = json.load(f)
    else:
        _cache = {}
    return _cache


def _save(data: dict[str, Any]) -> None:
    global _cache  # noqa: PLW0603
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)
    _cache = data


def get(key: str, default: Any = None) -> Any:
    """Get a setting value by key."""
    return _load().get(key, default)


def set(key: str, value: Any) -> None:  # noqa: A001
    """Set a setting value and persist."""
    data = _load().copy()
    data[key] = value
    _save(data)


def all_settings() -> dict[str, Any]:
    """Return all settings."""
    return _load().copy()


def reset_cache() -> None:
    """Clear the in-memory cache (for testing)."""
    global _cache  # noqa: PLW0603
    _cache = None

