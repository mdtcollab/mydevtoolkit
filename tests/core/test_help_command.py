from pathlib import Path

from mdt.commands.help import HelpCommand
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry


class DummyCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry


def test_help_command_lists_registered_names() -> None:
    registry = CommandRegistry()
    registry.register("help", DummyCommand)
    registry.register("git_branch", DummyCommand, category="git")
    registry.register_category("copilot")

    command = HelpCommand(registry)
    result = command(args=[], context=ProjectContext(cwd=Path("."), repo_root=None, project_name=None))

    assert result.success is True
    assert "Available commands:" in result.output
    assert "help" in result.output
    assert "[Built-in]" in result.output
    assert "[git]" in result.output
    assert "branch" in result.output
    assert "[copilot]" in result.output
    assert "(no commands yet)" in result.output

