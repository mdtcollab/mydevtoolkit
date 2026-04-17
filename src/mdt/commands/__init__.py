from mdt.commands.exit import ExitCommand
from mdt.commands.git_branch import GitBranchCommand
from mdt.commands.help import HelpCommand
from mdt.commands.openspec_branch import OpenspecBranchCommand
from mdt.commands.openspec_finish import OpenspecFinishCommand
from mdt.core.registry import CommandRegistry


def build_command_registry() -> CommandRegistry:
    registry = CommandRegistry()
    registry.register_category("openspec")
    registry.register_category("git")
    registry.register_category("copilot")
    registry.register("help", HelpCommand)
    registry.register("exit", ExitCommand)
    registry.register("openspec_branch", OpenspecBranchCommand, category="openspec")
    registry.register("openspec_finish", OpenspecFinishCommand, category="openspec")
    registry.register("git_branch", GitBranchCommand, category="git")
    return registry


COMMAND_REGISTRY = build_command_registry()
