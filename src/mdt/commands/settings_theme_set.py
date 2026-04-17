"""settings_theme_set command: select a UI theme for the shell."""
from __future__ import annotations

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult
from mdt.core.themes import ThemeRegistry, get_active_theme, set_active_theme


class SettingsThemeSetCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        self._theme_registry = ThemeRegistry()

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        if not args:
            return self._list_themes()
        theme_name = args[0].lower()
        return self._set_theme(theme_name)

    def _list_themes(self) -> CommandResult:
        themes = self._theme_registry.list_themes()
        active = get_active_theme()
        lines = ["Available themes:"]
        for t in themes:
            marker = " (active)" if t.name == active.name else ""
            lines.append(
                f"  {t.name}{marker}  "
                f"[{t.primary}]██[/{t.primary}] "
                f"[{t.secondary}]██[/{t.secondary}] "
                f"[{t.accent}]██[/{t.accent}] "
                f"[{t.surface}]██[/{t.surface}]"
            )
        lines.append("\nUsage: settings theme set <name>")
        return CommandResult(success=True, output="\n".join(lines))

    def _set_theme(self, name: str) -> CommandResult:
        try:
            set_active_theme(name)
        except ValueError:
            valid = ", ".join(t.name for t in self._theme_registry.list_themes())
            return CommandResult(
                success=False,
                error=f"Unknown theme '{name}'. Available: {valid}",
            )
        return CommandResult(
            success=True,
            output=f"Theme set to '{name}'",
            data={"theme": name},
        )

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        """Provide theme name completions."""
        registry = ThemeRegistry()
        names = [t.name for t in registry.list_themes()]
        if position == 0 or (tokens and len(tokens) <= 1):
            prefix = tokens[0].lower() if tokens else ""
            return [n for n in names if n.startswith(prefix)]
        return []

