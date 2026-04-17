# completion-input Specification

## Purpose
Define the completion-aware input widget for the mdt shell, including keybindings and suggestion display.

## Requirements
### Requirement: Tab key completes or advances the current suggestion
The completion input widget SHALL intercept the `Tab` key and, when completions are available, insert the common prefix or cycle through candidates.

#### Scenario: Single completion available on Tab
- **WHEN** the user types `"he"` and presses `Tab`
- **THEN** the input is updated to `"help"` (the single matching command)

#### Scenario: Multiple completions share a common prefix on Tab
- **WHEN** the user types `"git b"` and multiple sub-commands start with `b` sharing prefix `br`
- **THEN** the input is updated to `"git br"` (common prefix inserted)

#### Scenario: Multiple completions with no further common prefix on Tab
- **WHEN** the user types `"g"` and both `git` and `grep` are registered
- **THEN** the suggestions are displayed and input remains `"g"` until further refinement

### Requirement: Enter key accepts unambiguous completion
The completion input widget SHALL accept an unambiguous completion when the user presses `Enter` and exactly one candidate matches.

#### Scenario: Unambiguous completion on Enter
- **WHEN** the user types `"hel"` (only `help` matches) and presses `Enter`
- **THEN** the input is updated to `"help"` and submitted for execution

#### Scenario: Ambiguous completion on Enter
- **WHEN** the user types `"g"` (multiple matches) and presses `Enter`
- **THEN** the input is NOT auto-completed; the shell attempts to dispatch `"g"` as-is (which may fail)

### Requirement: Suggestions are displayed as the user types
The completion input widget SHALL display available completions incrementally as the user types, without requiring a keypress to trigger. Suggestions SHALL be rendered as a vertical list with one suggestion per line, with consistent padding, and visually distinct from the input area.

#### Scenario: Typing shows matching suggestions
- **WHEN** the user types `"op"`
- **THEN** a suggestion list showing `["openspec"]` is visible, rendered as individual rows

#### Scenario: No matches hides suggestions
- **WHEN** the user types `"xyz"` with no matching commands
- **THEN** no suggestion list is displayed

#### Scenario: Suggestions rendered as vertical list
- **WHEN** multiple suggestions are available
- **THEN** each suggestion is displayed on its own line with consistent left padding

### Requirement: Completion widget integrates with ShellScreen
The `ShellScreen` SHALL use the completion-aware input widget in place of the plain `Input` widget, wiring it to the `CompletionEngine`.

#### Scenario: Shell uses completion input
- **WHEN** the shell screen is composed
- **THEN** the prompt widget supports Tab completion and displays suggestions

### Requirement: Escape key dismisses suggestions without changing input
The completion input widget SHALL dismiss the suggestion display when the user presses `Escape`, leaving the current input text unchanged.

#### Scenario: Escape hides suggestions
- **WHEN** suggestions are visible and the user presses `Escape`
- **THEN** the suggestions are hidden and the input text remains as typed

### Requirement: Up arrow navigates to previous command in history
The completion input widget SHALL move backward through command history when the user presses the Up arrow key.

#### Scenario: Up arrow loads previous command
- **WHEN** the user has executed `"help"` and `"exit"`, and presses Up
- **THEN** the input is updated to `"exit"` (the most recent command)

#### Scenario: Up arrow at start of history stays at oldest
- **WHEN** the user has pressed Up to reach the oldest command and presses Up again
- **THEN** the input remains showing the oldest command

#### Scenario: Up arrow with empty history does nothing
- **WHEN** no commands have been executed and the user presses Up
- **THEN** the input remains unchanged

### Requirement: Down arrow navigates to next command in history
The completion input widget SHALL move forward through command history when the user presses the Down arrow key.

#### Scenario: Down arrow loads next command
- **WHEN** the user has pressed Up twice and then presses Down
- **THEN** the input is updated to the more recent command

#### Scenario: Down arrow past newest clears input
- **WHEN** the user has pressed Up once and then presses Down
- **THEN** the input is cleared (returns to empty/new command state)

### Requirement: CompletionInput accepts a CommandHistory instance
The `CompletionInput` SHALL accept a `CommandHistory` instance and use it for up/down arrow navigation.

#### Scenario: History wired to input
- **WHEN** the `CompletionInput` is created with a `CommandHistory`
- **THEN** up/down arrow keys navigate the provided history

