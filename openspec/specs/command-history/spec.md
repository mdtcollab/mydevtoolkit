# command-history Specification

## Purpose
Define the session-scoped command history storage and keyboard navigation behavior for the mdt shell.

## Requirements
### Requirement: CommandHistory stores executed commands in session order
The `CommandHistory` SHALL maintain an ordered list of commands added during the session.

#### Scenario: Adding commands
- **WHEN** `history.add("help")` and then `history.add("git branch")` are called
- **THEN** the history contains `["help", "git branch"]` in order

#### Scenario: Empty history
- **WHEN** no commands have been added
- **THEN** the history list is empty

### Requirement: CommandHistory supports backward navigation with previous()
The `CommandHistory` SHALL provide a `previous()` method that returns the prior command relative to the current cursor position, moving the cursor backward.

#### Scenario: Navigate backward from end
- **WHEN** history contains `["help", "exit"]` and `previous()` is called
- **THEN** the return value is `"exit"` (the most recent command)

#### Scenario: Navigate backward twice
- **WHEN** history contains `["help", "exit"]` and `previous()` is called twice
- **THEN** the first call returns `"exit"` and the second returns `"help"`

#### Scenario: Navigate backward past beginning
- **WHEN** the cursor is already at the oldest command and `previous()` is called
- **THEN** the return value is the oldest command (cursor does not move past the start)

#### Scenario: Navigate backward on empty history
- **WHEN** the history is empty and `previous()` is called
- **THEN** the return value is `None`

### Requirement: CommandHistory supports forward navigation with next()
The `CommandHistory` SHALL provide a `next()` method that returns the next command relative to the current cursor position, moving the cursor forward.

#### Scenario: Navigate forward after going back
- **WHEN** `previous()` has been called twice and then `next()` is called
- **THEN** the return value is the more recent of the two visited commands

#### Scenario: Navigate forward past end
- **WHEN** the cursor is already past the newest command and `next()` is called
- **THEN** the return value is `None` (indicating return to empty input)

### Requirement: CommandHistory resets cursor when a new command is added
The `CommandHistory` SHALL reset the navigation cursor to the end when `add()` is called.

#### Scenario: Cursor resets on add
- **WHEN** the user navigates backward and then a new command is added
- **THEN** the cursor resets so the next `previous()` returns the newly added command

### Requirement: CommandHistory does not store duplicate consecutive commands
The `CommandHistory` SHALL skip adding a command if it is identical to the most recently added command.

#### Scenario: Duplicate consecutive command
- **WHEN** `history.add("help")` is called twice consecutively
- **THEN** the history contains only one `"help"` entry

#### Scenario: Non-consecutive duplicate allowed
- **WHEN** `history.add("help")`, `history.add("exit")`, `history.add("help")` are called
- **THEN** the history contains `["help", "exit", "help"]`

### Requirement: CommandHistory does not store empty commands
The `CommandHistory` SHALL ignore empty or whitespace-only strings passed to `add()`.

#### Scenario: Empty string ignored
- **WHEN** `history.add("")` is called
- **THEN** the history remains unchanged

