from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, RichLog

from mdt.core.completion import CompletionEngine
from mdt.core.dispatcher import CommandDispatcher
from mdt.core.history import CommandHistory
from mdt.core.registry import CommandRegistry
from mdt.core.themes import get_active_theme
from mdt.ui.completion_input import CompletionInput

ASCII_HEADER = """\
  ███╗   ███╗██████╗ ████████╗
  ████╗ ████║██╔══██╗╚══██╔══╝
  ██╔████╔██║██║  ██║   ██║   
  ██║╚██╔╝██║██║  ██║   ██║   
  ██║ ╚═╝ ██║██████╔╝   ██║   
  ╚═╝     ╚═╝╚═════╝    ╚═╝    MyDevToolkit"""

HELP_SUMMARY = "Type [bold]help[/bold] for commands.  Categories: [cyan]openspec[/cyan]  [cyan]git[/cyan]  [cyan]copilot[/cyan]  [cyan]settings[/cyan]"


class ShellScreen(Screen[None]):
    DEFAULT_CSS = """
    ShellScreen {
        layout: vertical;
    }
    #header {
        height: auto;
        padding: 1 2;
    }
    #help-summary {
        height: auto;
        padding: 0 2 1 2;
    }
    #activity {
        border: solid $panel;
        margin: 0 1;
        min-height: 5;
    }
    #prompt {
        dock: bottom;
        margin: 1 0;
    }
    """

    def __init__(self, dispatcher: CommandDispatcher, registry: CommandRegistry) -> None:
        super().__init__()
        self._dispatcher = dispatcher
        self._engine = CompletionEngine(registry)
        self._history = CommandHistory()

    def compose(self) -> ComposeResult:
        yield Label(ASCII_HEADER, id="header")
        yield Label(HELP_SUMMARY, id="help-summary", markup=True)
        yield RichLog(id="activity", wrap=True, highlight=True, markup=True)
        yield CompletionInput(engine=self._engine, placeholder="Enter command", id="prompt", history=self._history)

    def on_mount(self) -> None:
        self._apply_theme()
        self.query_one("#prompt", CompletionInput).focus()

    def _apply_theme(self) -> None:
        """Apply the active theme colors to all shell zones."""
        theme = get_active_theme()
        self.query_one("#header", Label).styles.color = theme.primary
        self.query_one("#help-summary", Label).styles.color = theme.secondary
        activity = self.query_one("#activity", RichLog)
        activity.styles.border = ("solid", theme.accent)
        prompt = self.query_one("#prompt", CompletionInput)
        prompt.styles.border = ("solid", theme.surface)
        self._current_accent = theme.accent

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command_text = event.value.strip()
        prompt = self.query_one("#prompt", CompletionInput)
        activity = self.query_one("#activity", RichLog)
        accent = getattr(self, "_current_accent", "cyan")

        if command_text:
            self._history.add(command_text)
            activity.write(f"[{accent}]>[/{accent}] {command_text}")
            result = self._dispatcher.dispatch(command_text)

            if result.output:
                style = "green" if result.success else "red"
                activity.write(f"[{style}]{result.output}[/{style}]")

            if result.error:
                activity.write(f"[red]{result.error}[/red]")

            if result.data.get("theme"):
                self._apply_theme()

            if result.exit_requested:
                self.app.exit()

        prompt.value = ""
        prompt.focus()
