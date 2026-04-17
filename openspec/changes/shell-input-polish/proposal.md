## Why

The mdt interactive shell works functionally but the input experience feels rough. IntelliSense suggestions are displayed as plain inline text, the command textbox has a slight left-margin misalignment, and there is no command history navigation. These polish issues make the shell feel like a prototype rather than a usable developer console. Improving these areas makes the shell more productive and pleasant for repeated daily use.

## What Changes

- Improve the visual presentation of IntelliSense completion suggestions with better spacing, highlighting, and a more polished dropdown-style display
- Fix the command textbox layout alignment so it sits cleanly within the shell without the slight right-shift/left-margin gap
- Improve the command textbox styling for a more polished appearance
- Add session-scoped command history storage that records executed commands
- Add up/down arrow key navigation through command history in the input widget

## Capabilities

### New Capabilities
- `command-history`: Define the command history storage and keyboard navigation behavior for the shell session

### Modified Capabilities
- `completion-input`: The completion input widget gains improved suggestion display styling and up/down arrow history navigation
- `shell-screen-layout`: The shell screen layout gains improved command textbox alignment and styling

## Impact

- Modified file: `src/mdt/ui/completion_input.py` (suggestion display styling, history navigation keybindings)
- Modified file: `src/mdt/ui/shell_screen.py` (textbox alignment CSS, history integration)
- New or modified tests: `tests/ui/test_completion_input.py`, `tests/ui/test_shell_screen.py`
- No new dependencies required — all changes use Textual's existing CSS and widget capabilities

