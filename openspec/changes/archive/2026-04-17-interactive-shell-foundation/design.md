## Context

MyDevToolkit has no runtime interface today. The project needs a foundation that:
- Launches a persistent interactive shell via `mdt`
- Detects project/repository context automatically
- Provides a clean extension point for future command categories

This is a greenfield Python package (`src/mdt/`) built on Textual for the TUI layer.

## Goals / Non-Goals

**Goals:**
- Strict separation between headless core and Textual UI so the core is testable without a display
- Single entry point: `mdt` launches the shell; no other top-level subcommands
- Command lifecycle: input → registry lookup → dispatch → `CommandResult` → rendered output
- Built-in commands: `help` and `exit` only
- Project layout and interfaces designed so future command categories drop in without touching UI code

**Non-Goals:**
- Any domain commands (OpenSpec, Git, GitHub Copilot, etc.)
- One-shot CLI flags or subcommands (`mdt openspec`, `mdt git …`)
- Plugin loading from external packages (may come later)
- Persistent command history across sessions (can be added later)

## Decisions

### 1. `src/` layout
**Decision**: Use `src/mdt/` with `pyproject.toml`.  
**Rationale**: Prevents accidental imports of the package from the repo root during development; standard for modern Python projects.  
**Alternative considered**: Flat `mdt/` at root — simpler but causes import shadowing issues with editable installs.

### 2. Headless core in `src/mdt/core/`
**Decision**: All business logic lives in `core/` with zero Textual imports.  
**Rationale**: Core can be unit-tested with plain `pytest` and no display server. UI is a thin adapter.  
**Modules**: `context.py`, `result.py`, `registry.py`, `dispatcher.py`.

### 3. `CommandResult` dataclass with `exit_requested` sentinel
**Decision**: `CommandResult` carries `success: bool`, `output: str`, `error: str | None`, `data: dict`, `exit_requested: bool = False`.  
**Rationale**: Uniform return type from dispatcher — UI only needs to inspect one object; no exceptions cross the UI/core boundary.  
**Alternative considered**: Raising a custom `ExitException` — leaks control-flow concerns into the UI and complicates testing.

### 4. Explicit command registration in `commands/__init__.py`
**Decision**: Commands are registered by explicit imports in `src/mdt/commands/__init__.py`, not via decorators or entry-point discovery.  
**Rationale**: Simple, deterministic, easy to read. Discovery patterns add complexity before it's needed.  
**Alternative considered**: `@registry.register` decorator — requires a global registry singleton accessible at definition time, which complicates isolated unit tests.

### 5. `CommandRegistry` as a plain class (not a global singleton)
**Decision**: `CommandRegistry` is instantiated in `MdtApp.__init__` and passed explicitly to `CommandDispatcher`.  
**Rationale**: Avoids global state; each test can create its own registry without teardown.

### 6. Textual `RichLog` + `Input` layout
**Decision**: `ShellScreen` composes a `RichLog` (output history, scrollable) above a single-line `Input` widget.  
**Rationale**: Textual's built-in widgets; minimal custom CSS needed. `RichLog` supports Rich markup for coloured results.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Textual API changes between versions | Pin `textual>=0.60` in `pyproject.toml`; review changelog on upgrades |
| Large output floods the `RichLog` | Acceptable for v1; pagination or truncation can be added later |
| `src/` layout unfamiliar to contributors | Document in `README`; standard tooling (pip, pytest) handles it transparently |
| Command name collisions as registry grows | Registry raises `ValueError` on duplicate registration; caught early in tests |

