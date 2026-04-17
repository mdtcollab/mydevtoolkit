# MyDevToolkit (mdt)

MyDevToolkit is a shell-first developer toolkit. Running `mdt` launches a persistent interactive Textual shell for project-aware commands.

## Prerequisites

- Python 3.11+
- `pip`

## Install

```bash
pip install -e .[dev]
```

## Run

```bash
mdt
```

The shell stays open for repeated commands. Built-in commands in this first version:

- `help`
- `exit`

## Project Layout

- `src/mdt/core/`: headless business logic (`ProjectContext`, `CommandResult`, registry, dispatcher)
- `src/mdt/commands/`: command handlers and built-in command registration
- `src/mdt/ui/`: thin Textual UI (`MdtApp`, `ShellScreen`)
- `tests/core/`: unit tests for headless core
- `tests/ui/`: UI smoke test

## Adding New Commands

1. Add a new command handler class in `src/mdt/commands/`.
2. Register it in `src/mdt/commands/__init__.py`.
3. Add focused tests in `tests/core/`.

No UI redesign is required when adding commands; the shell uses the central registry and dispatcher.

