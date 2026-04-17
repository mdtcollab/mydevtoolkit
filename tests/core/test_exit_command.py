from pathlib import Path

from mdt.commands.exit import ExitCommand
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry


def test_exit_command_sets_exit_requested() -> None:
    command = ExitCommand(CommandRegistry())

    result = command(args=[], context=ProjectContext(cwd=Path("."), repo_root=None, project_name=None))

    assert result.success is True
    assert result.exit_requested is True
    assert result.output == "Goodbye."

