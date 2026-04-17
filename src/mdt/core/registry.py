"""Command registry for storing and discovering shell commands."""


class CommandRegistry:
    """Central registry for shell commands and their metadata.

    Stores command handlers by name with optional category grouping.
    Supports completion by exposing methods to query matching commands
    and delegate argument completion to handlers.
    """

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

    def get_completions(self, prefix: str) -> list[str]:
        """Return command names and category prefixes matching the given prefix.

        If prefix contains a space (e.g., "git "), returns sub-commands for that category.
        """
        prefix_lower = prefix.strip().lower()

        # Check if prefix is a category followed by space (e.g., "git ")
        if " " in prefix:
            parts = prefix_lower.split(None, 1)
            if parts:
                category = parts[0]
                sub_prefix = parts[1] if len(parts) > 1 else ""
                # Find commands in this category and return their sub-command names
                candidates = []
                for name, cat in self._categories.items():
                    if cat == category and name.startswith(f"{category}_"):
                        sub_cmd = name[len(category) + 1:]  # Remove "category_" prefix
                        if sub_cmd.lower().startswith(sub_prefix):
                            candidates.append(sub_cmd)
                return sorted(candidates)

        # Return matching command names and category names
        candidates = set()

        # Add matching command names (excluding category-prefixed ones for top-level)
        for name in self._handlers:
            if name.startswith(prefix_lower):
                # For categorized commands, show just the category at top level
                cat = self._categories.get(name)
                if cat and name.startswith(f"{cat}_"):
                    candidates.add(cat)
                else:
                    candidates.add(name)

        # Add matching category names
        for cat in self._declared_categories:
            if cat.startswith(prefix_lower):
                candidates.add(cat)

        return sorted(candidates)

    def get_argument_completions(
        self, command_name: str, position: int, tokens: list[str]
    ) -> list[str]:
        """Return argument completions from a command handler's get_completions method.

        If the handler does not implement get_completions, returns an empty list.
        """
        handler_cls = self._handlers.get(command_name.strip().lower())
        if handler_cls is None:
            return []

        get_completions_method = getattr(handler_cls, "get_completions", None)
        if get_completions_method is None or not callable(get_completions_method):
            return []

        try:
            return list(get_completions_method(position, tokens))
        except Exception:  # noqa: BLE001
            return []
