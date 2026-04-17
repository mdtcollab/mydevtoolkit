class CommandRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, type] = {}

    def register(self, name: str, handler: type) -> None:
        normalized = name.strip().lower()
        if not normalized:
            raise ValueError("Command name cannot be empty")
        if normalized in self._handlers:
            raise ValueError(f"Command '{normalized}' is already registered")
        self._handlers[normalized] = handler

    def resolve(self, name: str) -> type | None:
        return self._handlers.get(name.strip().lower())

    def names(self) -> frozenset[str]:
        return frozenset(self._handlers.keys())

