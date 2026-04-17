## Why

The mdt shell currently requires users to know and type commands exactly. Without completion support, users must memorize available commands, sub-commands, and options—or repeatedly invoke `help`. Adding IntelliSense-style completion enables command discovery directly in the input flow, reduces typing errors, and aligns with modern shell and IDE experiences.

## What Changes

- Add a completion engine that generates suggestions from the registered command structure
- Integrate completion into the shell's command input, surfacing suggestions as the user types
- Enable `Tab` to complete or advance the current suggestion
- Enable `Enter` to accept an unambiguous completion when one exists
- Surface multiple matches clearly so users can refine input incrementally
- Keep completion logic decoupled from UI presentation

## Capabilities

### New Capabilities
- `completion-engine`: Core logic for generating completions from registered commands, sub-commands, and known options
- `completion-input`: UI integration that wires the completion engine into the shell's input widget, handling Tab/Enter keybindings and displaying suggestions

### Modified Capabilities
- `command-registry`: Extend to expose structured metadata (e.g., sub-commands, known options) so the completion engine can enumerate valid tokens at each position

## Impact

- **Code**: New modules in `src/mdt/core/` (completion engine) and `src/mdt/ui/` (input integration)
- **Existing Commands**: Command handlers may optionally declare known options for richer completion
- **Tests**: New unit tests for completion logic and integration tests for keybinding behavior
- **Dependencies**: No new external dependencies expected; leverages Textual's existing input and key handling

