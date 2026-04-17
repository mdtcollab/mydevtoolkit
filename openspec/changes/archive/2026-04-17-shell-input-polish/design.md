## Context

The mdt shell uses Textual for its TUI. The `CompletionInput` widget wraps a Textual `Input` with a `SuggestionDisplay` (a `Static` widget) that shows suggestions as space-separated plain text. The command textbox (`#prompt`) is docked to the bottom with `margin: 1`, causing a slight left/right offset. There is no command history — each command is fire-and-forget from the input perspective.

## Goals / Non-Goals

**Goals:**
- Make the suggestion display look like a proper dropdown/menu with per-item rows, highlighting, and clear visual separation
- Fix the command textbox left-margin alignment so it sits flush with the shell content area
- Apply consistent styling to the textbox for a polished look
- Add a `CommandHistory` class that stores executed commands for the session
- Wire up/down arrow keys in `CompletionInput` to navigate history

**Non-Goals:**
- Persisting history across sessions (file-based history)
- Fuzzy search or history filtering
- Mouse-based suggestion selection
- Changing the completion engine logic or the command registry

## Decisions

### 1. SuggestionDisplay renders suggestions as vertical list items
Instead of joining suggestions with spaces, each suggestion will be rendered on its own line with consistent padding. The active/highlighted suggestion (if cycling) can be visually distinguished. This uses Textual Rich markup — no new widgets needed.

**Alternative**: Use a `ListView` widget — rejected as over-engineered for a simple list of strings.

### 2. CommandHistory is a standalone headless class
`CommandHistory` lives in `mdt/core/` as a simple list-based store with a cursor. It exposes `add(cmd)`, `previous()`, `next()`, and `reset_cursor()`. This keeps history logic testable outside the UI.

**Alternative**: Embed history directly in `CompletionInput` — rejected to maintain the thin-UI/headless-core pattern.

### 3. Up/Down arrows in CompletionInput navigate history when suggestions are not visible
When the suggestion list is hidden (no active completions), up/down arrows navigate command history. When suggestions are visible, up/down could navigate suggestions in the future, but for now they navigate history (suggestions use Tab cycling). This avoids conflicting keybindings.

### 4. Fix textbox alignment with CSS changes only
The `#prompt` margin will be adjusted from `margin: 1` to `margin: 1 0` (vertical margin only, no horizontal) and left padding removed to align with the activity log area. This is a CSS-only fix.

## Risks / Trade-offs

- [History size] → Unbounded list for session scope is fine; sessions are short-lived. No cap needed initially.
- [Arrow key conflict] → Up/down arrows in Textual `Input` normally move the cursor. We intercept them at the `CompletionInput` level before they reach the inner Input, which is acceptable since the input is single-line (no vertical cursor movement).

