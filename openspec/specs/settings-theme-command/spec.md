# settings-theme-command Specification

## Purpose
Define the behavior of the `settings theme set` command for listing and applying UI themes.

## Requirements
### Requirement: Settings theme set command lists available themes
When invoked without arguments, the `settings theme set` command SHALL return a `CommandResult` listing all available theme names.

#### Scenario: List themes
- **WHEN** the user submits `settings theme set` with no additional arguments
- **THEN** a `CommandResult` with `success=True` is returned and `output` contains all built-in theme names

### Requirement: Settings theme set command applies a named theme
When invoked with a theme name argument, the command SHALL set the active theme and return a success result.

#### Scenario: Apply valid theme
- **WHEN** the user submits `settings theme set ocean`
- **THEN** the active theme is changed to `"ocean"` and a `CommandResult` with `success=True` and a confirmation message is returned

#### Scenario: Apply unknown theme
- **WHEN** the user submits `settings theme set nonexistent`
- **THEN** a `CommandResult` with `success=False` and an error listing valid theme names is returned

### Requirement: Command posts ThemeChanged message
After successfully changing the theme, the command result SHALL include `data={"theme": "<name>"}` so the shell can detect the change and update styling.

#### Scenario: Result data contains theme name
- **WHEN** a theme is successfully set
- **THEN** `result.data["theme"]` equals the newly active theme name

