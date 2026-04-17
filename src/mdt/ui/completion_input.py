"""Completion-aware input widget for the mdt shell."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, Static
from textual.binding import Binding
from textual import events

from mdt.core.completion import CompletionEngine
from mdt.core.history import CommandHistory


class SuggestionDisplay(Static):
    """Displays completion suggestions above the input."""

    DEFAULT_CSS = """
    SuggestionDisplay {
        height: auto;
        max-height: 8;
        padding: 0;
        margin: 0 1;
        background: $surface-darken-1;
        color: $text;
        border: tall $primary-background-darken-1;
        display: none;
    }
    SuggestionDisplay.visible {
        display: block;
    }
    """

    def set_suggestions(self, suggestions: list[str]) -> None:
        """Update the displayed suggestions as a vertical list."""
        if suggestions:
            display_list = suggestions[:10]
            lines = [f"  {s}" for s in display_list]
            if len(suggestions) > 10:
                lines.append(f"  [dim]… and {len(suggestions) - 10} more[/dim]")
            self.update("\n".join(lines))
            self.add_class("visible")
        else:
            self.update("")
            self.remove_class("visible")


class CompletionInput(Container):
    """Input widget with IntelliSense-style completion support.

    Wraps a Textual Input widget and adds:
    - Suggestion display as the user types
    - Tab key to complete or advance through candidates
    - Enter key to accept unambiguous completion before submission
    - Escape key to dismiss suggestions
    """

    DEFAULT_CSS = """
    CompletionInput {
        height: auto;
        layout: vertical;
    }
    CompletionInput > Input {
        margin: 0;
        border: tall $accent;
    }
    """

    BINDINGS = [
        Binding("tab", "complete", "Complete", show=False),
        Binding("escape", "dismiss_suggestions", "Dismiss", show=False),
        Binding("up", "history_previous", "Previous", show=False),
        Binding("down", "history_next", "Next", show=False),
    ]

    def __init__(
        self,
        engine: CompletionEngine,
        placeholder: str = "Enter command",
        id: str | None = None,
        history: CommandHistory | None = None,
    ) -> None:
        super().__init__(id=id)
        self._engine = engine
        self._placeholder = placeholder
        self._suggestions: list[str] = []
        self._suggestion_index = 0
        self._history = history or CommandHistory()

    def compose(self) -> ComposeResult:
        yield SuggestionDisplay(id="suggestions")
        yield Input(placeholder=self._placeholder, id="input")

    @property
    def input(self) -> Input:
        """Return the underlying Input widget."""
        return self.query_one("#input", Input)

    @property
    def value(self) -> str:
        """Return the current input value."""
        return self.input.value

    @value.setter
    def value(self, val: str) -> None:
        """Set the input value."""
        self.input.value = val

    def focus(self) -> None:
        """Focus the input widget."""
        self.input.focus()

    def on_mount(self) -> None:
        """Focus input when mounted."""
        self.input.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update suggestions when input changes."""
        if event.input.id == "input":
            self._update_suggestions()

    def _update_suggestions(self) -> None:
        """Query engine and update suggestion display."""
        self._suggestions = self._engine.get_completions(self.input.value)
        self._suggestion_index = 0
        suggestion_display = self.query_one("#suggestions", SuggestionDisplay)
        suggestion_display.set_suggestions(self._suggestions)

    def action_complete(self) -> None:
        """Handle Tab key: complete or cycle through suggestions."""
        if not self._suggestions:
            return

        current_value = self.input.value

        if len(self._suggestions) == 1:
            # Single suggestion: complete it
            self._apply_completion(self._suggestions[0])
        else:
            # Multiple suggestions: find common prefix
            common = self._common_prefix(self._suggestions)

            # Get the current token being completed
            current_token = self._get_current_token()

            if common and len(common) > len(current_token):
                # Extend with common prefix
                self._apply_completion(common)
            else:
                # Cycle through suggestions
                suggestion = self._suggestions[self._suggestion_index]
                self._apply_completion(suggestion)
                self._suggestion_index = (self._suggestion_index + 1) % len(self._suggestions)

    def action_dismiss_suggestions(self) -> None:
        """Handle Escape key: dismiss suggestions."""
        self._suggestions = []
        suggestion_display = self.query_one("#suggestions", SuggestionDisplay)
        suggestion_display.set_suggestions([])

    def action_history_previous(self) -> None:
        """Handle Up arrow: navigate to previous command in history."""
        cmd = self._history.previous()
        if cmd is not None:
            self.input.value = cmd
            self.input.cursor_position = len(cmd)

    def action_history_next(self) -> None:
        """Handle Down arrow: navigate to next command in history."""
        cmd = self._history.next()
        if cmd is not None:
            self.input.value = cmd
            self.input.cursor_position = len(cmd)
        else:
            self.input.value = ""

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key: accept unambiguous completion before bubbling."""
        if event.input.id == "input":
            if len(self._suggestions) == 1:
                # Unambiguous completion: apply it before submission
                self._apply_completion(self._suggestions[0])
                # Update the event value
                event.value = self.input.value
            # Clear suggestions
            self._suggestions = []
            suggestion_display = self.query_one("#suggestions", SuggestionDisplay)
            suggestion_display.set_suggestions([])

    def _apply_completion(self, completion: str) -> None:
        """Apply a completion to the current input."""
        current = self.input.value
        tokens = current.split()

        if not tokens:
            # Empty input: just set the completion
            self.input.value = completion + " "
        elif current.endswith(" "):
            # Space at end: append the completion
            self.input.value = current + completion + " "
        else:
            # Replace the last token with the completion
            prefix = " ".join(tokens[:-1])
            if prefix:
                self.input.value = prefix + " " + completion + " "
            else:
                self.input.value = completion + " "

        # Move cursor to end
        self.input.cursor_position = len(self.input.value)

        # Update suggestions for the new value
        self._update_suggestions()

    def _get_current_token(self) -> str:
        """Get the token currently being typed."""
        current = self.input.value
        if not current or current.endswith(" "):
            return ""
        tokens = current.split()
        return tokens[-1] if tokens else ""

    @staticmethod
    def _common_prefix(strings: list[str]) -> str:
        """Find the longest common prefix of a list of strings."""
        if not strings:
            return ""
        prefix = strings[0]
        for s in strings[1:]:
            while not s.lower().startswith(prefix.lower()):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix

