"""Tests for CompletionInput widget."""
from __future__ import annotations

import pytest

from mdt.core.completion import CompletionEngine
from mdt.core.history import CommandHistory
from mdt.core.registry import CommandRegistry
from mdt.ui.completion_input import CompletionInput, SuggestionDisplay


class DummyCommand:
    """Command handler without completions."""

    def __init__(self, registry: CommandRegistry) -> None:
        del registry


class CommandWithCompletions:
    """Command handler that implements get_completions."""

    def __init__(self, registry: CommandRegistry) -> None:
        del registry

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        if position == 0:
            prefix = tokens[0].lower() if tokens else ""
            options = ["bugfix", "chore", "feature", "hotfix", "refactor"]
            return [opt for opt in options if opt.startswith(prefix)]
        return []


def make_engine() -> CompletionEngine:
    """Create a completion engine with test commands."""
    registry = CommandRegistry()
    registry.register("help", DummyCommand)
    registry.register("exit", DummyCommand)
    registry.register("git_branch", CommandWithCompletions, category="git")
    registry.register_category("openspec")
    return CompletionEngine(registry)


class TestSuggestionDisplay:
    """Tests for SuggestionDisplay widget."""

    def test_set_suggestions_with_items_shows_display(self) -> None:
        display = SuggestionDisplay()
        display.set_suggestions(["help", "exit"])
        assert display.has_class("visible")

    def test_set_suggestions_empty_hides_display(self) -> None:
        display = SuggestionDisplay()
        display.set_suggestions(["help"])
        display.set_suggestions([])
        assert not display.has_class("visible")

    def test_set_suggestions_truncates_long_list(self) -> None:
        display = SuggestionDisplay()
        many_suggestions = [f"item{i}" for i in range(15)]
        display.set_suggestions(many_suggestions)
        # Should show "... and 5 more" - check internal _content
        content = str(display.render())
        assert "and 5 more" in content


class TestCompletionInputCommonPrefix:
    """Tests for the common prefix calculation."""

    def test_common_prefix_single_item(self) -> None:
        result = CompletionInput._common_prefix(["feature"])
        assert result == "feature"

    def test_common_prefix_multiple_items(self) -> None:
        result = CompletionInput._common_prefix(["branch", "browse"])
        assert result == "br"

    def test_common_prefix_no_common(self) -> None:
        result = CompletionInput._common_prefix(["alpha", "beta"])
        assert result == ""

    def test_common_prefix_empty_list(self) -> None:
        result = CompletionInput._common_prefix([])
        assert result == ""

    def test_common_prefix_case_insensitive(self) -> None:
        result = CompletionInput._common_prefix(["Feature", "feature"])
        assert result.lower() == "feature"


class TestCompletionInputHistory:
    """Tests for history navigation in CompletionInput."""

    def test_accepts_history_parameter(self) -> None:
        engine = make_engine()
        history = CommandHistory()
        widget = CompletionInput(engine=engine, history=history)
        assert widget._history is history

    def test_default_history_created_if_none(self) -> None:
        engine = make_engine()
        widget = CompletionInput(engine=engine)
        assert widget._history is not None
