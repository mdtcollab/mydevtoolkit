"""settings_editor_set command: configure the preferred editor for MDT."""

from __future__ import annotations

from mdt.core import settings
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult

KNOWN_EDITORS = ["code --wait", "nano", "nvim", "vim", "vi", "emacs", "micro", "helix"]


class SettingsEditorSetCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del context
        if not args:
            current = settings.get("editor")
            if current:
                return CommandResult(success=True, output=f"Current editor: {current}")
            return CommandResult(
                success=True,
                output="No editor configured. Using $EDITOR or fallback (nano → vi).\n"
                       f"Set with: settings editor set <editor>\n"
                       f"Examples: {', '.join(KNOWN_EDITORS)}",
            )

        editor = " ".join(args)
        settings.set("editor", editor)
        return CommandResult(
            success=True,
            output=f"Editor set to: {editor}",
        )

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        if position == 0:
            prefix = tokens[0].lower() if tokens else ""
            return [e for e in KNOWN_EDITORS if e.startswith(prefix)]
        return []

