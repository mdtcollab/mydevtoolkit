from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class ExitCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args, context
        return CommandResult(success=True, output="Goodbye.", exit_requested=True)

