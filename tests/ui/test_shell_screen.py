import pytest
from textual.widgets import Input, RichLog

from mdt.ui.app import MdtApp


@pytest.mark.asyncio
async def test_shell_screen_help_and_exit() -> None:
    app = MdtApp()

    async with app.run_test() as pilot:
        await pilot.press("h", "e", "l", "p", "enter")
        await pilot.pause()

        output = app.screen.query_one("#output", RichLog)
        assert len(output.lines) > 0

        prompt = app.screen.query_one("#prompt", Input)
        assert prompt.value == ""

        await pilot.press("e", "x", "i", "t", "enter")
        await pilot.pause()

    assert app.is_running is False


