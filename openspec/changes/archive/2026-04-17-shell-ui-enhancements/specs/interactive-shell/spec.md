## MODIFIED Requirements

### Requirement: Shell launches on `mdt` invocation
Running `mdt` SHALL start the Textual interactive shell and keep it open until the user issues `exit` or sends an interrupt signal. The shell screen SHALL display the four-zone layout (header, help summary, activity log, command input).

#### Scenario: Shell starts with structured layout
- **WHEN** the user runs `mdt` in a terminal
- **THEN** the Textual shell screen is displayed with an ASCII art header, a help summary, an empty activity log, and a focused command input textbox

#### Scenario: Shell persists across commands
- **WHEN** the user submits a command
- **THEN** the shell remains open, the activity log is updated, and the input textbox is cleared and refocused

#### Scenario: Shell exits on `exit` command
- **WHEN** the user submits `exit`
- **THEN** the shell closes and control returns to the OS terminal

