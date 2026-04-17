import pytest

from mdt.core.registry import CommandRegistry


class DummyCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry


def test_register_resolve_and_names() -> None:
    registry = CommandRegistry()

    registry.register("help", DummyCommand)
    registry.register("exit", DummyCommand)

    assert registry.resolve("help") is DummyCommand
    assert registry.resolve("unknown") is None
    assert registry.names() == frozenset({"help", "exit"})


def test_register_duplicate_raises_value_error() -> None:
    registry = CommandRegistry()
    registry.register("help", DummyCommand)

    with pytest.raises(ValueError):
        registry.register("help", DummyCommand)

