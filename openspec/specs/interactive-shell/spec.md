# interactive-shell Specification

## Purpose
Define the persistent shell-first entrypoint for MyDevToolkit.

## Requirements
### Requirement: Shell launches on `mdt` invocation
Running `mdt` SHALL start the Textual interactive shell and keep it open until the user issues `exit` or sends an interrupt signal. The shell screen SHALL display the four-zone layout: header, help summary, activity log, and command input.

#### Scenario: Shell starts with structured layout
- **WHEN** the user runs `mdt` in a terminal
- **THEN** the Textual shell screen is displayed with an ASCII art header, a help summary, an empty activity log, and a focused command input textbox

#### Scenario: Shell persists across commands
- **WHEN** the user submits a command
- **THEN** the shell remains open, the activity log is updated, and the input textbox is cleared and refocused

#### Scenario: Shell exits on `exit` command
- **WHEN** the user submits `exit`
- **THEN** the shell closes and control returns to the OS terminal

### Requirement: No other top-level CLI subcommands
`mdt` SHALL NOT expose one-shot subcommands (e.g., `mdt openspec`, `mdt git`). The only effect of invoking `mdt` SHALL be launching the interactive shell.

#### Scenario: No subcommand flag
- **WHEN** the user runs `mdt --help` or `mdt <anything>`
- **THEN** the shell launches (or a brief usage hint is shown directing them to the shell)

