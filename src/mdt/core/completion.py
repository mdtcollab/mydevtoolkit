"""Completion engine for generating IntelliSense-style suggestions."""
from __future__ import annotations

from mdt.core.registry import CommandRegistry


class CompletionEngine:
    """Generates completion candidates based on registry and input text."""

    def __init__(self, registry: CommandRegistry) -> None:
        self._registry = registry

    def get_completions(self, input_text: str) -> list[str]:
        """Return completion candidates for the given input text.

        Handles:
        - Command-level completion (empty input or partial command prefix)
        - Sub-command completion (category prefix followed by space)
        - Argument-level completion (delegating to command handlers)

        All matching is case-insensitive and results are sorted alphabetically.
        """
        text = input_text.strip()

        # Empty input: return all top-level commands and categories
        if not text:
            return self._registry.get_completions("")

        tokens = text.split()

        # Single token: could be partial command or category
        if len(tokens) == 1:
            # Check if there's a trailing space (user completed the first token)
            if input_text.endswith(" "):
                return self._get_after_first_token(tokens[0])
            # Still typing the first token
            return self._registry.get_completions(text)

        # Multiple tokens: determine context
        first_token = tokens[0].lower()

        # Check if first token is a category
        if first_token in self._registry.categories():
            # Second token position: could be sub-command or argument
            if len(tokens) == 2 and not input_text.endswith(" "):
                # Still typing sub-command
                return self._registry.get_completions(input_text)

            # Past sub-command: try argument completion
            # Find the full command name (category_subcommand)
            sub_cmd = tokens[1].lower()
            command_name = f"{first_token}_{sub_cmd}"

            # Calculate argument position and get the current token being typed
            arg_position = len(tokens) - 3  # After "category subcommand"
            if input_text.endswith(" "):
                arg_position += 1
                current_token = ""
            else:
                current_token = tokens[-1]

            if arg_position >= 0:
                completions = self._registry.get_argument_completions(
                    command_name, arg_position, [current_token] if current_token else []
                )
                # Filter by current token prefix (case-insensitive)
                if current_token:
                    prefix = current_token.lower()
                    completions = [c for c in completions if c.lower().startswith(prefix)]
                return sorted(completions)

        # First token is a standalone command
        command_name = first_token
        if self._registry.resolve(command_name):
            # Try argument completion
            arg_position = len(tokens) - 2  # After the command itself
            if input_text.endswith(" "):
                arg_position += 1
                current_token = ""
            else:
                current_token = tokens[-1]

            if arg_position >= 0:
                completions = self._registry.get_argument_completions(
                    command_name, arg_position, [current_token] if current_token else []
                )
                # Filter by current token prefix (case-insensitive)
                if current_token:
                    prefix = current_token.lower()
                    completions = [c for c in completions if c.lower().startswith(prefix)]
                return sorted(completions)

        # No completions available
        return []

    def _get_after_first_token(self, first_token: str) -> list[str]:
        """Get completions after the first token is complete."""
        first_lower = first_token.lower()

        # If first token is a category, return sub-commands
        if first_lower in self._registry.categories():
            return self._registry.get_completions(f"{first_lower} ")

        # If first token is a standalone command, return argument completions
        if self._registry.resolve(first_lower):
            return self._registry.get_argument_completions(first_lower, 0, [])

        return []

