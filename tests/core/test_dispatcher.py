from dataclasses import dataclass
from pathlib import Path

from mdt.core.context import ProjectContext
from mdt.core.dispatcher import CommandDispatcher
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


@dataclass
class EchoCommand:
    registry: CommandRegistry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del context
        return CommandResult(success=True, output=" ".join(args))


@dataclass
class BoomCommand:
    registry: CommandRegistry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args, context
        raise RuntimeError("boom")


def _context() -> ProjectContext:
    return ProjectContext(cwd=Path("/tmp"), repo_root=None, project_name=None)


def test_dispatch_known_command_returns_success() -> None:
    registry = CommandRegistry()
    registry.register("echo", EchoCommand)
    dispatcher = CommandDispatcher(registry, _context())

    result = dispatcher.dispatch("echo hello world")

    assert result.success is True
    assert result.output == "hello world"


def test_dispatch_unknown_command_returns_failed_result() -> None:
    dispatcher = CommandDispatcher(CommandRegistry(), _context())

    result = dispatcher.dispatch("unknown")

    assert result.success is False
    assert result.error == "Unknown command: unknown"


def test_dispatch_blank_input_returns_noop_success() -> None:
    dispatcher = CommandDispatcher(CommandRegistry(), _context())

    result = dispatcher.dispatch("   ")

    assert result.success is True
    assert result.output == ""


def test_dispatch_catches_command_exception() -> None:
    registry = CommandRegistry()
    registry.register("boom", BoomCommand)
    dispatcher = CommandDispatcher(registry, _context())

    result = dispatcher.dispatch("boom")

    assert result.success is False
    assert "boom" in (result.error or "")


def test_dispatch_two_word_command_returns_success() -> None:
    registry = CommandRegistry()
    registry.register("git_branch", EchoCommand, category="git")
    dispatcher = CommandDispatcher(registry, _context())

    result = dispatcher.dispatch("git branch feature abc-123 login page")

    assert result.success is True
    assert result.output == "feature abc-123 login page"


def test_dispatch_unknown_two_word_command_returns_failed_result() -> None:
    dispatcher = CommandDispatcher(CommandRegistry(), _context())

    result = dispatcher.dispatch("openspec unknown")

    assert result.success is False
    assert result.error == "Unknown command: openspec unknown"


