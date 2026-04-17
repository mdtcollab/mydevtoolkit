class CommandRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, type] = {}
        self._categories: dict[str, str | None] = {}
        self._declared_categories: dict[str, None] = {}

    def register_category(self, name: str) -> None:
        normalized = name.strip().lower()
        if not normalized:
            raise ValueError("Category name cannot be empty")
        self._declared_categories.setdefault(normalized, None)

    def register(self, name: str, handler: type, category: str | None = None) -> None:
        normalized = name.strip().lower()
        if not normalized:
            raise ValueError("Command name cannot be empty")
        if normalized in self._handlers:
            raise ValueError(f"Command '{normalized}' is already registered")
        self._handlers[normalized] = handler
        normalized_category = category.strip().lower() if category else None
        if normalized_category is not None:
            self.register_category(normalized_category)
        self._categories[normalized] = normalized_category

    def resolve(self, name: str) -> type | None:
        return self._handlers.get(name.strip().lower())

    def names(self) -> frozenset[str]:
        return frozenset(self._handlers.keys())

    def all(self) -> list[tuple[str, type, str | None]]:
        return [(name, self._handlers[name], self._categories[name]) for name in self._handlers]

    def categories(self) -> tuple[str, ...]:
        return tuple(self._declared_categories.keys())

