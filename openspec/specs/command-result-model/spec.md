# command-result-model Specification

## Purpose
TBD - created by archiving change interactive-shell-foundation. Update Purpose after archive.
## Requirements
### Requirement: CommandResult carries success status
Every `CommandResult` SHALL have a `success: bool` field indicating whether the command completed without error.

#### Scenario: Successful result
- **WHEN** a command completes normally
- **THEN** `CommandResult.success` is `True`

#### Scenario: Failed result
- **WHEN** a command fails or an exception is caught
- **THEN** `CommandResult.success` is `False`

### Requirement: CommandResult carries human-readable output
`CommandResult.output: str` SHALL contain the text to display in the shell's output area. It MAY be empty.

#### Scenario: Output present
- **WHEN** a command produces output
- **THEN** `CommandResult.output` contains that text

### Requirement: CommandResult carries an optional error message
`CommandResult.error: str | None` SHALL contain an error description when `success=False`, and SHALL be `None` when `success=True`.

#### Scenario: Error message on failure
- **WHEN** `success=False`
- **THEN** `CommandResult.error` is a non-empty string describing the failure

### Requirement: CommandResult carries an exit_requested sentinel
`CommandResult.exit_requested: bool` (default `False`) SHALL be set to `True` only by the `exit` command to signal the shell to close.

#### Scenario: Exit sentinel set by exit command
- **WHEN** the `exit` command is dispatched
- **THEN** the returned `CommandResult.exit_requested` is `True`

#### Scenario: Exit sentinel not set by normal commands
- **WHEN** any command other than `exit` is dispatched
- **THEN** the returned `CommandResult.exit_requested` is `False`

### Requirement: CommandResult carries optional structured data
`CommandResult.data: dict` SHALL default to an empty dict when not explicitly provided. It MAY carry structured payload for future use by UI components or callers that understand the specific command output.

#### Scenario: Data defaults to empty dict
- **WHEN** a `CommandResult` is created without specifying `data`
- **THEN** `CommandResult.data` equals `{}`

