from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CommandDispatcher:
    def __init__(self, registry: CommandRegistry, context: ProjectContext) -> None:
        self._registry = registry
        self._context = context

    def dispatch(self, raw: str) -> CommandResult:
        stripped = raw.strip()
        if not stripped:
            return CommandResult(success=True)

        tokens = stripped.split()
        command_name, args = tokens[0], tokens[1:]
        handler_cls = self._registry.resolve(command_name)
        if handler_cls is None:
            return CommandResult(
                success=False,
                error=f"Unknown command: {command_name}",
            )

        try:
            handler = handler_cls(self._registry)
            return handler(args=args, context=self._context)
        except Exception as exc:  # noqa: BLE001
            return CommandResult(success=False, error=str(exc))

