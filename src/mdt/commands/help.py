from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class HelpCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        self._registry = registry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args, context
        names = sorted(self._registry.names())
        if not names:
            return CommandResult(success=True, output="No commands registered.")
        lines = ["Available commands:"] + [f"- {name}" for name in names]
        return CommandResult(success=True, output="\n".join(lines))

