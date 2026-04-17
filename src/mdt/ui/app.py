from textual.app import App

from mdt.commands import COMMAND_REGISTRY
from mdt.core.context import ProjectContext
from mdt.core.dispatcher import CommandDispatcher
from mdt.ui.shell_screen import ShellScreen


class MdtApp(App[None]):
    TITLE = "MyDevToolkit"

    def __init__(self) -> None:
        super().__init__()
        context = ProjectContext.detect()
        dispatcher = CommandDispatcher(COMMAND_REGISTRY, context)
        self._shell_screen = ShellScreen(dispatcher=dispatcher)

    def on_mount(self) -> None:
        self.push_screen(self._shell_screen)

