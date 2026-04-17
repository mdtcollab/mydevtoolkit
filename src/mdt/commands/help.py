from collections import defaultdict

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class HelpCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        self._registry = registry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args, context
        all_cmds = self._registry.all()
        categories = self._registry.categories()
        if not all_cmds and not categories:
            return CommandResult(success=True, output="No commands registered.")

        grouped: dict[str, list[str]] = defaultdict(list)
        for name, _, category in sorted(all_cmds, key=lambda x: (x[2] or "", x[0])):
            grouped[category or "Built-in"].append(self._display_name(name, category))

        for category in categories:
            grouped.setdefault(category, [])

        lines = ["Available commands:"]
        ordered_groups = ["Built-in", *[category for category in categories if category in grouped]]
        ordered_groups.extend(
            group_name
            for group_name in sorted(grouped.keys())
            if group_name not in ordered_groups
        )
        for group_name in ordered_groups:
            if group_name not in grouped:
                continue
            lines.append(f"\n[{group_name}]")
            if grouped[group_name]:
                for cmd in grouped[group_name]:
                    lines.append(f"  {cmd}")
            else:
                lines.append("  (no commands yet)")
        return CommandResult(success=True, output="\n".join(lines))

    @staticmethod
    def _display_name(name: str, category: str | None) -> str:
        if category and name.startswith(f"{category}_"):
            return name.removeprefix(f"{category}_").replace("_", " ")
        return name.replace("_", " ")

