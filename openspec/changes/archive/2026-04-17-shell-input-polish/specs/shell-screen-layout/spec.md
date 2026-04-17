## MODIFIED Requirements

### Requirement: Shell screen has four vertical zones
The `ShellScreen` SHALL render four zones stacked vertically: (1) ASCII art header, (2) short help summary, (3) activity/timeline log, (4) command input textbox. The command input textbox SHALL be aligned flush with the content area without horizontal margin offset.

#### Scenario: All zones visible on launch
- **WHEN** the user runs `mdt`
- **THEN** the screen shows an ASCII art header at the top, a help summary below it, a scrollable activity log below that, and a command input box at the bottom

#### Scenario: Command textbox is horizontally aligned
- **WHEN** the shell screen is composed
- **THEN** the command input textbox has no extra left or right margin, sitting flush with the shell layout

### Requirement: Command input box is always focused
The command input textbox SHALL receive keyboard focus on startup and after each command is submitted. After submission, the command SHALL be recorded in the session command history.

#### Scenario: Input ready after launch
- **WHEN** the shell screen finishes composing
- **THEN** the command input textbox has focus and accepts keystrokes

#### Scenario: Input refocused after command
- **WHEN** the user submits any command
- **THEN** the textbox is cleared, the command is added to history, and focus returns to it

