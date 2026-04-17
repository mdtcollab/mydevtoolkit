## Context

The mdt shell uses a `CommandRegistry` that stores commands by name with optional categories. The `CommandDispatcher` parses raw input, resolves handlers, and executes them. The UI layer (`ShellScreen`) uses a simple Textual `Input` widget for command entry. Currently there is no completion support—users must type commands exactly or use `help` to discover them.

Commands are registered at startup via `build_command_registry()`. Some commands (like `git branch`) have known argument tokens (e.g., category prefixes like `feature`, `bugfix`). This metadata is currently implicit in command implementations rather than exposed through the registry.

## Goals / Non-Goals

**Goals:**
- Provide IntelliSense-style completion for commands, sub-commands, and known options
- Make completion registry-aware so it scales automatically with new commands
- Support incremental completion as the user types
- Handle `Tab` to complete/advance and `Enter` to accept unambiguous completions
- Keep completion logic testable and decoupled from UI presentation

**Non-Goals:**
- Dynamic argument completion (e.g., filesystem paths, git branches from remote)
- Fuzzy matching or ranking algorithms
- Completion for values that are not predefined and enumerable
- Changes to the command execution flow or result handling

## Decisions

### Decision 1: Introduce a CompletionEngine class in core layer

The completion engine will be a pure-logic class that takes the current input text and cursor position, queries the registry for valid tokens, and returns completion candidates. This keeps completion testable without UI dependencies.

**Alternatives considered:**
- Embedding completion logic in the Input widget: rejected because it couples presentation to business logic and makes testing harder.
- Using Textual's built-in `Suggester`: considered, but it doesn't natively support position-aware multi-token completion; a custom approach integrates better with our registry.

### Decision 2: Extend CommandRegistry to expose completion metadata

Commands will optionally declare a `completions` class attribute or method that returns known options/arguments for each argument position. The registry will expose a method to retrieve completable tokens given a command prefix.

**Alternatives considered:**
- Hardcoding completions in the UI: rejected per requirements—completions must come from registered command structure.
- Separate completion registry: adds complexity; extending the existing registry keeps the single source of truth.

### Decision 3: Create a CompletionInput widget that wraps Input

A custom widget extending or wrapping Textual's `Input` will intercept `Tab` and `Enter` keys, invoke the completion engine, and display suggestions. This isolates keybinding and display logic from the engine.

**Alternatives considered:**
- Modifying ShellScreen directly: rejected because it would mix concerns; a dedicated widget is more composable and testable.

### Decision 4: Display suggestions inline or in a dropdown overlay

For multiple matches, show a brief list of candidates (e.g., in a small overlay or as inline hints). Single unambiguous matches complete immediately on `Tab` or `Enter`.

**Alternatives considered:**
- Always show popup menu: heavier UI; inline hints are lighter for a shell-first tool.
- No visual feedback until Tab: less discoverable; showing suggestions as the user types improves UX.

### Decision 5: Completion protocol for commands

Define a simple protocol: command classes may implement a `get_completions(position: int, tokens: list[str]) -> list[str]` method. The engine calls this when the user is past the command/sub-command tokens. Commands without this method offer no argument completion.

**Alternatives considered:**
- Decorator-based registration: more magic; explicit method is clearer.
- Mandatory completion support: rejected; many commands have dynamic or unbounded arguments.

## Risks / Trade-offs

- **[Risk] Completion metadata maintenance**: Commands must opt-in to declare completions; missing metadata means no suggestions. → Mitigation: Document the protocol; provide examples; fallback gracefully.
- **[Risk] Key binding conflicts**: `Tab` and `Enter` have existing semantics in Textual widgets. → Mitigation: Override only when completion context applies; pass through otherwise.
- **[Risk] Performance with many commands**: Prefix matching on every keystroke could slow down. → Mitigation: Registry is small; simple string prefix filtering is O(n) but n is tiny; optimize only if needed.

