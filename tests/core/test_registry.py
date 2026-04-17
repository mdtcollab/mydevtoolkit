import pytest

from mdt.core.registry import CommandRegistry


class DummyCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry


def test_register_resolve_and_names() -> None:
    registry = CommandRegistry()

    registry.register("help", DummyCommand)
    registry.register("exit", DummyCommand, category="builtins")

    assert registry.resolve("help") is DummyCommand
    assert registry.resolve("unknown") is None
    assert registry.names() == frozenset({"help", "exit"})
    assert registry.all() == [
        ("help", DummyCommand, None),
        ("exit", DummyCommand, "builtins"),
    ]
    assert registry.categories() == ("builtins",)


def test_register_duplicate_raises_value_error() -> None:
    registry = CommandRegistry()
    registry.register("help", DummyCommand)

    with pytest.raises(ValueError):
        registry.register("help", DummyCommand)


def test_register_category_exposes_empty_categories() -> None:
    registry = CommandRegistry()

    registry.register_category("copilot")

    assert registry.categories() == ("copilot",)


class TestGetCompletions:
    """Tests for CommandRegistry.get_completions method."""

    def test_empty_prefix_returns_all_commands_and_categories(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        registry.register("exit", DummyCommand)
        registry.register_category("git")
        registry.register_category("openspec")

        result = registry.get_completions("")

        assert result == ["exit", "git", "help", "openspec"]

    def test_partial_prefix_filters_commands(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        registry.register("exit", DummyCommand)

        result = registry.get_completions("he")

        assert result == ["help"]

    def test_category_prefix_returns_sub_commands(self) -> None:
        registry = CommandRegistry()
        registry.register("git_branch", DummyCommand, category="git")
        registry.register("git_status", DummyCommand, category="git")

        result = registry.get_completions("git ")

        assert result == ["branch", "status"]

    def test_category_with_sub_prefix_filters_sub_commands(self) -> None:
        registry = CommandRegistry()
        registry.register("git_branch", DummyCommand, category="git")
        registry.register("git_status", DummyCommand, category="git")

        result = registry.get_completions("git br")

        assert result == ["branch"]

    def test_categorized_commands_show_category_at_top_level(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)
        registry.register("git_branch", DummyCommand, category="git")

        result = registry.get_completions("g")

        assert result == ["git"]

    def test_no_matches_returns_empty_list(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)

        result = registry.get_completions("xyz")

        assert result == []

    def test_case_insensitive_matching(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)

        result = registry.get_completions("HE")

        assert result == ["help"]


class CommandWithCompletions:
    """Command handler that implements get_completions."""

    def __init__(self, registry: CommandRegistry) -> None:
        del registry

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        if position == 0:
            prefix = tokens[0] if tokens else ""
            options = ["feature", "bugfix", "hotfix"]
            return [opt for opt in options if opt.startswith(prefix.lower())]
        return []


class TestGetArgumentCompletions:
    """Tests for CommandRegistry.get_argument_completions method."""

    def test_handler_with_get_completions_method(self) -> None:
        registry = CommandRegistry()
        registry.register("test_cmd", CommandWithCompletions)

        result = registry.get_argument_completions("test_cmd", 0, ["fe"])

        assert result == ["feature"]

    def test_handler_without_get_completions_method(self) -> None:
        registry = CommandRegistry()
        registry.register("help", DummyCommand)

        result = registry.get_argument_completions("help", 0, [])

        assert result == []

    def test_unknown_command_returns_empty_list(self) -> None:
        registry = CommandRegistry()

        result = registry.get_argument_completions("unknown", 0, [])

        assert result == []

    def test_empty_prefix_returns_all_options(self) -> None:
        registry = CommandRegistry()
        registry.register("test_cmd", CommandWithCompletions)

        result = registry.get_argument_completions("test_cmd", 0, [])

        assert result == ["feature", "bugfix", "hotfix"]
