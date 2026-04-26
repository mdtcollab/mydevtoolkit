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

The shell stays open for repeated commands and now includes:

- an ASCII art header
- a short help summary with top-level categories
- an activity/timeline pane for command history and results
- a persistent command input at the bottom
- **IntelliSense-style completion**: suggestions appear as you type

## Command Completion

The shell supports Tab completion for commands, sub-commands, and known options:

- **Tab**: Complete or advance the current suggestion
- **Enter**: Accept an unambiguous completion and execute
- **Escape**: Dismiss suggestions without changing input

Completions are driven by the command registry—new commands automatically gain completion support. Commands can optionally declare argument completions (e.g., `git branch` suggests category prefixes like `feature`, `bugfix`).

Initial commands and categories:

- `help`
- `exit`
- `openspec branch`
- `git branch <category> <ticket> <description...>`
- `workflow status`
- `workflow record workflow_type=<...> command_id=<...> raw_command=<...> success=<true|false> ...`

Top-level categories currently shown in the shell:

- `openspec`
- `git`
- `copilot` (reserved for future helpers)
- `workflow`

## Workflow Event Ingestion

MDT can record workflow events from external AI coding agent hooks so `workflow status` can prefer tracked history over inference for the reported last command.

Project-local workflow events are stored under `.mdt/workflow-history.jsonl`.

For headless integrations, use the dedicated ingestion entrypoint:

```bash
mdt-workflow-event \
  --project-root . \
  --workflow-type openspec \
  --command-id apply \
  --raw-command /opsx:apply \
  --success true \
  --change-name my-change \
  --source agent-hook
```

You can also record events inside the interactive shell with `workflow record` using `key=value` arguments.

## Project Layout

- `src/mdt/core/`: headless business logic (`ProjectContext`, `CommandResult`, registry, dispatcher)
- `src/mdt/commands/`: command handlers and built-in command registration
- `src/mdt/ui/`: thin Textual UI (`MdtApp`, `ShellScreen` with header/help/activity/input layout)
- `tests/core/`: unit tests for headless core
- `tests/ui/`: UI smoke test

## Adding New Commands

1. Add a new command handler class in `src/mdt/commands/`.
2. Register it in `src/mdt/commands/__init__.py`, optionally under a category.
3. Add focused tests in `tests/core/`.

No UI redesign is required when adding commands; the shell uses the central registry and dispatcher.

