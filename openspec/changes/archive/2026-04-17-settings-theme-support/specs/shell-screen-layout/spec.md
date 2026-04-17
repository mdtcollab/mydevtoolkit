## MODIFIED Requirements

### Requirement: Shell screen has four vertical zones
The `ShellScreen` SHALL render four zones stacked vertically: (1) ASCII art header, (2) short help summary, (3) activity/timeline log, (4) command input textbox. The command input textbox SHALL be aligned flush with the content area without horizontal margin offset. Zone styles SHALL be derived from the active theme rather than hardcoded color values.

#### Scenario: All zones visible on launch
- **WHEN** the user runs `mdt`
- **THEN** the screen shows an ASCII art header at the top, a help summary below it, a scrollable activity log below that, and a command input box at the bottom, all styled according to the active theme

#### Scenario: Command textbox is horizontally aligned
- **WHEN** the shell screen is composed
- **THEN** the command input textbox has no extra left or right margin, sitting flush with the shell layout

### Requirement: Help summary is static
The help summary zone SHALL display a single-line or two-line hint listing available command categories including `settings` and how to get more help.

#### Scenario: Hint visible below header
- **WHEN** the shell screen is composed
- **THEN** the hint text is visible beneath the header and includes the `settings` category

