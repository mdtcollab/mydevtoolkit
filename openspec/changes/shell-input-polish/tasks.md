## 1. Command History Core

- [ ] 1.1 Create `src/mdt/core/history.py` with `CommandHistory` class implementing `add()`, `previous()`, `next()`, and `reset_cursor()`
- [ ] 1.2 Handle duplicate consecutive commands and empty command filtering in `add()`
- [ ] 1.3 Create `tests/core/test_history.py` with tests for add, previous, next, cursor reset, duplicate filtering, and empty input

## 2. IntelliSense Visual Polish

- [ ] 2.1 Update `SuggestionDisplay` in `completion_input.py` to render suggestions as a vertical list (one per line) with consistent padding and improved styling
- [ ] 2.2 Update `SuggestionDisplay` CSS for polished appearance: border, background contrast, padding, and max-height

## 3. Command Textbox Alignment and Styling

- [ ] 3.1 Update `ShellScreen` CSS for `#prompt` to remove horizontal margin offset and align flush with the content area
- [ ] 3.2 Polish the command input CSS for consistent visual appearance

## 4. History Navigation in CompletionInput

- [ ] 4.1 Update `CompletionInput.__init__` to accept an optional `CommandHistory` parameter
- [ ] 4.2 Add up/down arrow key handlers in `CompletionInput` that navigate history and update the input value
- [ ] 4.3 Update `tests/ui/test_completion_input.py` with tests for history navigation via up/down arrows

## 5. Integration

- [ ] 5.1 Update `ShellScreen` to create a `CommandHistory` instance, pass it to `CompletionInput`, and call `history.add()` on command submission
- [ ] 5.2 Update `tests/ui/test_shell_screen.py` with tests for history integration

