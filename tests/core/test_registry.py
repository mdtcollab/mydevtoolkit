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


