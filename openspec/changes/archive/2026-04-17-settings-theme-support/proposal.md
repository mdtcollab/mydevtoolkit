## Why

The mdt interactive shell currently has no user-facing settings or visual customization. Adding a `settings` category with theme support lets users personalize their shell experience and establishes the foundation for future preference commands. Predefined pastel themes keep the UI readable while giving users meaningful visual choice.

## What Changes

- Add a new top-level `settings` command category to the command registry
- Add a `settings theme set` command that presents predefined themes and applies the selection
- Define at least 5 built-in pastel themes, each containing exactly 4 coordinated colors
- Apply the selected theme's colors to shell UI elements (header, help summary, activity log accents, input styling)
- Store the active theme in-memory for the current session

## Capabilities

### New Capabilities
- `theme-registry`: Defines the built-in theme catalog — theme data model, at least 5 pastel themes with 4 colors each, and lookup/listing API
- `settings-theme-command`: The `settings theme set` command that lists available themes, lets the user select one, and triggers a theme change
- `theme-application`: Applies the active theme's color palette to shell UI elements (header, help area, activity log, input) so the visual change is coherent

### Modified Capabilities
- `command-categories`: Add the `settings` category so it appears in help output and command routing
- `shell-screen-layout`: Shell screen zones must accept dynamic styling from the active theme rather than using only hardcoded styles

## Impact

- `src/mdt/commands/` — new `settings_theme_set.py` command module
- `src/mdt/core/` — new `themes.py` module for theme catalog and active-theme state
- `src/mdt/ui/shell_screen.py` — updated to read and apply active theme colors
- `src/mdt/__main__.py` — register `settings_theme_set` command under `settings` category
- `tests/` — new tests for theme registry, settings command, and theme application

