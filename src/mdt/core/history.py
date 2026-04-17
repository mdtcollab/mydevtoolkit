"""Session-scoped command history with cursor-based navigation."""
from __future__ import annotations


class CommandHistory:
    """Stores executed commands and supports up/down arrow navigation."""

    def __init__(self) -> None:
        self._commands: list[str] = []
        self._cursor: int = 0

    @property
    def commands(self) -> list[str]:
        """Return the list of stored commands."""
        return list(self._commands)

    def add(self, command: str) -> None:
        """Add a command to history. Ignores empty/whitespace and consecutive duplicates."""
        if not command or not command.strip():
            return
        if self._commands and self._commands[-1] == command:
            self._cursor = len(self._commands)
            return
        self._commands.append(command)
        self._cursor = len(self._commands)

    def previous(self) -> str | None:
        """Move cursor backward and return that command, or None if empty."""
        if not self._commands:
            return None
        if self._cursor > 0:
            self._cursor -= 1
        return self._commands[self._cursor]

    def next(self) -> str | None:
        """Move cursor forward and return that command, or None if past end."""
        if not self._commands:
            return None
        if self._cursor < len(self._commands) - 1:
            self._cursor += 1
            return self._commands[self._cursor]
        # Past the end — return to "new command" state
        self._cursor = len(self._commands)
        return None

    def reset_cursor(self) -> None:
        """Reset cursor to the end (past newest command)."""
        self._cursor = len(self._commands)

