## Why

MyDevToolkit (`mdt`) currently has no runtime interface. Developers need a persistent, project-aware shell to discover and run toolkit commands interactively — not a one-shot CLI with endless subcommands. Building the interactive shell foundation now establishes the architectural skeleton that all future command categories (OpenSpec, Git, GitHub Copilot helpers) will grow into.

## What Changes

- Introduce the `mdt` command as the single entry point that launches an interactive Textual shell session
- Add a headless core layer: `ProjectContext` detection, `CommandResult` model, `CommandRegistry`, and `CommandDispatcher`
- Add a Textual UI layer: `MdtApp` and `ShellScreen` with command input and scrollable output area
- Implement two built-in commands: `help` and `exit`
- Scaffold the Python project structure (`pyproject.toml`, `src/mdt/` layout, entry point)

## Capabilities

### New Capabilities

- `interactive-shell`: Textual-based persistent shell session launched by `mdt`; accepts repeated commands until `exit` is issued
- `project-context`: Automatic detection of repository root (`.git` walk-up), project name, and working directory on startup; made available to all commands
- `command-registry`: Central registry mapping command names to handler classes; supports incremental registration without UI changes
- `command-dispatcher`: Resolves raw user input to a registered command, injects `ProjectContext`, executes, and returns a structured `CommandResult`; catches all exceptions into a failed result
- `command-result-model`: Typed `CommandResult` dataclass with `success`, `output`, `error`, `data`, and `exit_requested` fields

### Modified Capabilities

## Impact

- New Python package `mdt` under `src/mdt/`; requires Python ≥ 3.11 and `textual` as a runtime dependency
- No existing code is modified; this is a greenfield addition
- `pyproject.toml` gains `[project.scripts]` entry `mdt = "mdt.__main__:main"`
- Test infrastructure (`pytest`, `pytest-asyncio`) added as dev dependencies

