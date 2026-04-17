# theme-application Specification

## Purpose
Define how the active theme's colors are applied to shell UI zones.

## Requirements
### Requirement: Shell screen applies active theme colors on mount
The `ShellScreen` SHALL read the active theme on mount and apply its colors to the four UI zones: header gets `primary`, help summary gets `secondary`, activity border/echo gets `accent`, prompt gets `surface`.

#### Scenario: Theme colors visible on launch
- **WHEN** the shell screen is mounted
- **THEN** the header text color matches the active theme's `primary` value and other zones reflect their mapped theme colors

### Requirement: Shell screen updates styling when theme changes
When a command result contains `data["theme"]`, the `ShellScreen` SHALL re-read the active theme and update all zone styles accordingly.

#### Scenario: Theme change updates all zones
- **WHEN** a `settings theme set ocean` command completes successfully
- **THEN** the header, help summary, activity log, and prompt zone styles update to reflect the `ocean` theme colors

