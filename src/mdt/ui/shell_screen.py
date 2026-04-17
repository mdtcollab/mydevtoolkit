from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, RichLog

from mdt.core.dispatcher import CommandDispatcher


class ShellScreen(Screen[None]):
    def __init__(self, dispatcher: CommandDispatcher) -> None:
        super().__init__()
        self._dispatcher = dispatcher

    def compose(self) -> ComposeResult:
        yield RichLog(id="output", wrap=True, highlight=True, markup=True)
        yield Input(placeholder="Enter command", id="prompt")

    def on_mount(self) -> None:
        self.query_one("#prompt", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command_text = event.value
        prompt = self.query_one("#prompt", Input)
        output = self.query_one("#output", RichLog)

        output.write(f"[bold cyan]>[/bold cyan] {command_text}")
        result = self._dispatcher.dispatch(command_text)

        if result.output:
            style = "green" if result.success else "red"
            output.write(f"[{style}]{result.output}[/{style}]")

        if result.error:
            output.write(f"[red]{result.error}[/red]")

        prompt.value = ""

        if result.exit_requested:
            self.app.exit()

