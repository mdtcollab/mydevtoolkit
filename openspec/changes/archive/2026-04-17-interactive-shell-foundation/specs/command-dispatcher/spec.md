## ADDED Requirements

### Requirement: Raw input is tokenised and dispatched to a registered command
The `CommandDispatcher` SHALL split raw input on whitespace, treat the first token as the command name, resolve it from the registry, instantiate the handler, and call it with the remaining tokens as arguments and the `ProjectContext`.

#### Scenario: Known command dispatched successfully
- **WHEN** `dispatcher.dispatch("help")` is called and `help` is registered
- **THEN** the return value is a `CommandResult` with `success=True`

#### Scenario: Unknown command returns failed result
- **WHEN** `dispatcher.dispatch("frobnicate")` is called and `frobnicate` is not registered
- **THEN** the return value is a `CommandResult` with `success=False` and a human-readable `error` message

### Requirement: Exceptions inside commands are caught and returned as failed results
The dispatcher SHALL catch any unhandled exception raised by a command handler and return a `CommandResult` with `success=False` and the exception message in `error`. The shell session MUST NOT crash.

#### Scenario: Command raises an exception
- **WHEN** a registered command raises `RuntimeError("boom")`
- **THEN** the dispatcher returns a `CommandResult` with `success=False` and `error` containing `"boom"`

### Requirement: Empty input returns a no-op result
The `CommandDispatcher` SHALL return a successful no-op `CommandResult` for blank or whitespace-only input.

#### Scenario: Blank input
- **WHEN** `dispatcher.dispatch("   ")` is called
- **THEN** the return value is a `CommandResult` with `success=True` and empty `output`

