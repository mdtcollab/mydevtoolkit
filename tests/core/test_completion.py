"""Tests for CompletionEngine."""
from __future__ import annotations

from mdt.core.completion import CompletionEngine
from mdt.core.registry import CommandRegistry


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


class TestCompletionEngineCommandLevel:
    """Tests for command-level completion."""

    def test_empty_input_returns_all_commands_and_categories(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        registry.register("exit", DummyCommand)
        registry.register_category("git")
        registry.register_category("openspec")
        engine = CompletionEngine(registry)

        result = engine.get_completions("")

        assert result == ["exit", "git", "help", "openspec"]

    def test_partial_command_prefix_filters_candidates(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        registry.register("exit", DummyCommand)
        engine = CompletionEngine(registry)

        result = engine.get_completions("he")

        assert result == ["help"]

    def test_no_matches_returns_empty_list(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        engine = CompletionEngine(registry)

        result = engine.get_completions("xyz")

        assert result == []

    def test_case_insensitive_matching(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        engine = CompletionEngine(registry)

        result = engine.get_completions("HE")

        assert result == ["help"]


class TestCompletionEngineSubCommandLevel:
    """Tests for sub-command completion (category prefix followed by space)."""

    def test_category_followed_by_space_returns_sub_commands(self) -> None:
        registry = CommandRegistry()
        registry.register("git_branch", DummyCommand, category="git")
        registry.register("git_status", DummyCommand, category="git")
        engine = CompletionEngine(registry)

        result = engine.get_completions("git ")

        assert result == ["branch", "status"]

    def test_category_with_partial_sub_command_filters(self) -> None:
        registry = CommandRegistry()
        registry.register("git_branch", DummyCommand, category="git")
        registry.register("git_status", DummyCommand, category="git")
        engine = CompletionEngine(registry)

        result = engine.get_completions("git br")

        assert result == ["branch"]


class TestCompletionEngineArgumentLevel:
    """Tests for argument-level completion."""

    def test_command_with_declared_completions(self) -> None:
        registry = CommandRegistry()
        registry.register("git_branch", CommandWithCompletions, category="git")
        engine = CompletionEngine(registry)

        result = engine.get_completions("git branch fe")

        assert result == ["feature"]

    def test_command_with_trailing_space_gets_all_arg_completions(self) -> None:
        registry = CommandRegistry()
        registry.register("git_branch", CommandWithCompletions, category="git")
        engine = CompletionEngine(registry)

        result = engine.get_completions("git branch ")

        assert result == ["bugfix", "chore", "feature", "hotfix", "refactor"]

    def test_command_without_declared_completions_returns_empty(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        engine = CompletionEngine(registry)

        result = engine.get_completions("help ")

        assert result == []

    def test_standalone_command_argument_completion(self) -> None:
        registry = CommandRegistry()
        registry.register("test", CommandWithCompletions)
        engine = CompletionEngine(registry)

        result = engine.get_completions("test fe")

        assert result == ["feature"]


class TestCompletionEngineSortedOutput:
    """Tests for sorted output."""

    def test_results_are_sorted_alphabetically(self) -> None:
        registry = CommandRegistry()
        registry.register("zebra", DummyCommand)
        registry.register("alpha", DummyCommand)
        registry.register("beta", DummyCommand)
        engine = CompletionEngine(registry)

        result = engine.get_completions("")

        assert result == ["alpha", "beta", "zebra"]

