from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, RichLog

from mdt.core.dispatcher import CommandDispatcher

ASCII_HEADER = """\
  ███╗   ███╗██████╗ ████████╗
  ████╗ ████║██╔══██╗╚══██╔══╝
  ██╔████╔██║██║  ██║   ██║   
  ██║╚██╔╝██║██║  ██║   ██║   
  ██║ ╚═╝ ██║██████╔╝   ██║   
  ╚═╝     ╚═╝╚═════╝    ╚═╝    MyDevToolkit"""

HELP_SUMMARY = "Type [bold]help[/bold] for commands.  Categories: [cyan]openspec[/cyan]  [cyan]git[/cyan]  [cyan]copilot[/cyan]"


class ShellScreen(Screen[None]):
    DEFAULT_CSS = """
    ShellScreen {
        layout: vertical;
    }
    #header {
        height: auto;
        padding: 1 2;
        color: cyan;
    }
    #help-summary {
        height: auto;
        padding: 0 2 1 2;
        color: $text-muted;
    }
    #activity {
        border: solid $panel;
        margin: 0 1;
        min-height: 5;
    }
    #prompt {
        dock: bottom;
        margin: 1;
    }
    """

    def __init__(self, dispatcher: CommandDispatcher) -> None:
        super().__init__()
        self._dispatcher = dispatcher

    def compose(self) -> ComposeResult:
        yield Label(ASCII_HEADER, id="header")
        yield Label(HELP_SUMMARY, id="help-summary", markup=True)
        yield RichLog(id="activity", wrap=True, highlight=True, markup=True)
        yield Input(placeholder="Enter command", id="prompt")

    def on_mount(self) -> None:
        self.query_one("#prompt", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command_text = event.value.strip()
        prompt = self.query_one("#prompt", Input)
        activity = self.query_one("#activity", RichLog)

        if command_text:
            activity.write(f"[bold cyan]>[/bold cyan] {command_text}")
            result = self._dispatcher.dispatch(command_text)

            if result.output:
                style = "green" if result.success else "red"
                activity.write(f"[{style}]{result.output}[/{style}]")

            if result.error:
                activity.write(f"[red]{result.error}[/red]")

            if result.exit_requested:
                self.app.exit()

        prompt.value = ""
        prompt.focus()
