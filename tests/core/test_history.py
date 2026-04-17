"""Tests for CommandHistory."""
from __future__ import annotations

from mdt.core.history import CommandHistory


class TestAdd:
    def test_adds_commands_in_order(self):
        h = CommandHistory()
        h.add("help")
        h.add("git branch")
        assert h.commands == ["help", "git branch"]

    def test_empty_history(self):
        h = CommandHistory()
        assert h.commands == []

    def test_ignores_empty_string(self):
        h = CommandHistory()
        h.add("")
        assert h.commands == []

    def test_ignores_whitespace_only(self):
        h = CommandHistory()
        h.add("   ")
        assert h.commands == []

    def test_skips_consecutive_duplicates(self):
        h = CommandHistory()
        h.add("help")
        h.add("help")
        assert h.commands == ["help"]

    def test_allows_non_consecutive_duplicates(self):
        h = CommandHistory()
        h.add("help")
        h.add("exit")
        h.add("help")
        assert h.commands == ["help", "exit", "help"]


class TestPrevious:
    def test_returns_none_on_empty(self):
        h = CommandHistory()
        assert h.previous() is None

    def test_returns_most_recent(self):
        h = CommandHistory()
        h.add("help")
        h.add("exit")
        assert h.previous() == "exit"

    def test_navigate_backward_twice(self):
        h = CommandHistory()
        h.add("help")
        h.add("exit")
        assert h.previous() == "exit"
        assert h.previous() == "help"

    def test_stays_at_oldest(self):
        h = CommandHistory()
        h.add("help")
        h.add("exit")
        h.previous()
        h.previous()
        assert h.previous() == "help"


class TestNext:
    def test_returns_none_on_empty(self):
        h = CommandHistory()
        assert h.next() is None

    def test_forward_after_backward(self):
        h = CommandHistory()
        h.add("help")
        h.add("exit")
        h.previous()  # exit
        h.previous()  # help
        assert h.next() == "exit"

    def test_forward_past_end_returns_none(self):
        h = CommandHistory()
        h.add("help")
        h.previous()  # help
        assert h.next() is None

    def test_next_without_previous_returns_none(self):
        h = CommandHistory()
        h.add("help")
        assert h.next() is None


class TestCursorReset:
    def test_cursor_resets_on_add(self):
        h = CommandHistory()
        h.add("help")
        h.add("exit")
        h.previous()  # exit
        h.previous()  # help
        h.add("new")
        assert h.previous() == "new"

