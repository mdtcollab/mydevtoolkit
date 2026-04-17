from mdt.commands.exit import ExitCommand
from mdt.commands.help import HelpCommand
from mdt.core.registry import CommandRegistry


def build_command_registry() -> CommandRegistry:
    registry = CommandRegistry()
    registry.register("help", HelpCommand)
    registry.register("exit", ExitCommand)
    return registry


COMMAND_REGISTRY = build_command_registry()

