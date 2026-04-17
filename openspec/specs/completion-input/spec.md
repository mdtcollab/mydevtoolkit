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
The completion input widget SHALL display available completions incrementally as the user types, without requiring a keypress to trigger.

#### Scenario: Typing shows matching suggestions
- **WHEN** the user types `"op"`
- **THEN** a suggestion list or hint showing `["openspec"]` is visible

#### Scenario: No matches hides suggestions
- **WHEN** the user types `"xyz"` with no matching commands
- **THEN** no suggestion list is displayed

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

