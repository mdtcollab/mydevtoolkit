## Context

The mdt interactive shell uses Textual for its TUI. Commands are registered in a `CommandRegistry` with optional categories and dispatched via `CommandDispatcher`. The shell screen (`ShellScreen`) has four zones with hardcoded CSS styles. There is currently no settings infrastructure or theme system.

## Goals / Non-Goals

**Goals:**
- Introduce a `settings` command category with a `settings theme set` subcommand
- Define a `ThemeRegistry` holding at least 5 predefined pastel themes (4 colors each)
- Apply the active theme to shell UI zones via Textual reactive CSS
- Keep theme logic in a dedicated module, separate from command logic

**Non-Goals:**
- Persisting theme selection across sessions (future work)
- User-defined / custom themes
- Additional settings beyond theme selection
- Theming the completion dropdown or other advanced widgets

## Decisions

### 1. Theme data model — NamedTuple with 4 color slots

Each `Theme` is a `NamedTuple` with fields: `name`, `primary`, `secondary`, `accent`, `surface`. This is simple, immutable, and easy to test. A dict-based approach was considered but loses type safety.

### 2. Centralized ThemeRegistry module at `mdt/core/themes.py`

All built-in themes and the active-theme accessor live in one module. Commands import it; the shell screen reads from it. Alternative: store themes on the App instance — rejected because commands need access without coupling to Textual.

### 3. Module-level mutable state for active theme

`themes.py` exposes `get_active_theme()` and `set_active_theme(name)`. A module-level variable holds the current selection. This is the simplest approach for a single-process TUI. A more formal state store was considered but is over-engineering for session-only state.

### 4. Shell screen applies theme via `watch` + `mutate_reactive_styles`

`ShellScreen` reads the active theme on mount and when theme changes. It updates widget styles (color properties) programmatically. Textual's `reactive` or a message-based approach can propagate the change. The command posts a custom Textual message (`ThemeChanged`) that the screen handles.

### 5. Color mapping: 4 colors → 4 zones

- `primary` → header text color
- `secondary` → help summary text color
- `accent` → activity log border and command echo color
- `surface` → input/prompt area border or background tint

This creates a clear visual effect per-zone without over-complicating the mapping.

### 6. Command presents a numbered list for selection

`settings theme set` (no args) prints available themes with numbers. `settings theme set <name>` applies directly. This matches the existing command pattern where args are passed as a list.

## Risks / Trade-offs

- [Session-only state] Theme resets on restart → acceptable for v1; persistence is future scope
- [Hardcoded color values] Pastel hex values may render differently on some terminals → mitigation: use named Textual colors where possible, fallback to hex
- [Global mutable state] Module-level theme state is simple but not thread-safe → acceptable for single-threaded Textual app

