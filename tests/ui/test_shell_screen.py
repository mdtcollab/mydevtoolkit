import pytest
from textual.widgets import Input, Label, RichLog

from mdt.ui.app import MdtApp
from mdt.ui.completion_input import CompletionInput


@pytest.mark.asyncio
async def test_shell_screen_help_and_exit() -> None:
    app = MdtApp()

    async with app.run_test() as pilot:
        header = app.screen.query_one("#header", Label)
        help_summary = app.screen.query_one("#help-summary", Label)
        assert "MyDevToolkit" in str(header.render())
        assert "copilot" in str(help_summary.render())

        await pilot.press("h", "e", "l", "p", "enter")
        await pilot.pause()

        output = app.screen.query_one("#activity", RichLog)
        assert len(output.lines) > 0

        prompt = app.screen.query_one("#prompt", CompletionInput)
        assert prompt.value == ""

        await pilot.press("e", "x", "i", "t", "enter")
        await pilot.pause()

    assert app.is_running is False


@pytest.mark.asyncio
async def test_tab_completion_in_shell() -> None:
    """Test that Tab completion works in the shell context."""
    app = MdtApp()

    async with app.run_test() as pilot:
        prompt = app.screen.query_one("#prompt", CompletionInput)

        # Type partial command "hel" and press Tab
        await pilot.press("h", "e", "l")
        await pilot.pause()

        # Press Tab to complete
        await pilot.press("tab")
        await pilot.pause()

        # Should complete to "help "
        assert prompt.value.strip() == "help"

        # Clear and try category completion
        prompt.value = ""
        await pilot.press("g", "i", "t")
        await pilot.pause()
        await pilot.press("tab")
        await pilot.pause()

        # Should complete to "git " (with space for sub-command)
        assert prompt.value.strip() == "git"


@pytest.mark.asyncio
async def test_suggestions_display_while_typing() -> None:
    """Test that suggestions appear as user types."""
    app = MdtApp()

    async with app.run_test() as pilot:
        # Type "he" - should show suggestions
        await pilot.press("h", "e")
        await pilot.pause()

        # Check that suggestions display is visible
        from mdt.ui.completion_input import SuggestionDisplay

        suggestions = app.screen.query_one("#suggestions", SuggestionDisplay)
        assert suggestions.has_class("visible")


@pytest.mark.asyncio
async def test_command_history_navigation() -> None:
    """Test that up/down arrows navigate command history."""
    app = MdtApp()

    async with app.run_test() as pilot:
        # Execute two commands
        await pilot.press("h", "e", "l", "p", "enter")
        await pilot.pause()

        await pilot.press("e", "x", "i", "t")
        await pilot.pause()
        # Don't press enter for exit (it would close the app)
        # Instead clear and type a different command
        prompt = app.screen.query_one("#prompt", CompletionInput)
        prompt.value = ""

        await pilot.press("h", "e", "l", "p", "enter")
        await pilot.pause()

        # Now press up to get previous command
        await pilot.press("up")
        await pilot.pause()

        assert prompt.value == "help"
