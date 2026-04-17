## 1. Theme Registry Module

- [x] 1.1 Create `src/mdt/core/themes.py` with `Theme` named tuple (`name`, `primary`, `secondary`, `accent`, `surface`)
- [x] 1.2 Define at least 5 built-in pastel themes in a `BUILTIN_THEMES` list
- [x] 1.3 Implement `ThemeRegistry` class with `list_themes()` and `get_theme(name)` methods
- [x] 1.4 Implement module-level `get_active_theme()` and `set_active_theme(name)` functions with default theme
- [x] 1.5 Add tests for theme data model, listing, lookup, active theme get/set, and unknown theme error

## 2. Settings Theme Set Command

- [x] 2.1 Create `src/mdt/commands/settings_theme_set.py` with `SettingsThemeSetCommand` class
- [x] 2.2 Implement no-args path: list available themes in output
- [x] 2.3 Implement named-arg path: set active theme and return success with `data={"theme": name}`
- [x] 2.4 Implement unknown theme path: return error with valid theme names
- [x] 2.5 Add tests for all three command paths (list, set valid, set invalid)

## 3. Command Registration

- [x] 3.1 Register `settings` category in `src/mdt/commands/__init__.py`
- [x] 3.2 Register `settings_theme_set` command under `settings` category
- [x] 3.3 Update `HELP_SUMMARY` in `shell_screen.py` to include `settings` category

## 4. Theme Application in Shell Screen

- [x] 4.1 Update `ShellScreen.on_mount` to read active theme and apply colors to header, help summary, activity, and prompt zones
- [x] 4.2 Add `_apply_theme` helper method that maps theme colors to widget styles
- [x] 4.3 Update `on_input_submitted` to detect `data["theme"]` in command result and call `_apply_theme`
- [x] 4.4 Replace hardcoded `cyan` color in header CSS and command echo with theme-derived colors
- [x] 4.5 Add tests for theme application logic
