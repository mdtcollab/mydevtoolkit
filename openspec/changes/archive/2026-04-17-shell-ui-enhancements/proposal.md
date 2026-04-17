## Why

The initial mdt shell launched successfully but presents a bare command prompt with no visible structure or guidance. Adding a header, help section, activity timeline, and command categories gives users immediate context, improves discoverability, and creates the scaffolding needed for the first real helper commands.

## What Changes

- Replace the plain shell layout with a structured four-zone screen: ASCII art header → short help section → activity/timeline window → command input textbox
- Add three top-level command categories: `openspec`, `git`, and `copilot`
- Add a `openspec branch` helper that reads the latest OpenSpec change folder name and creates + checks out a matching git branch
- Add a `git branch` helper that accepts free-text input, normalises it into a `<category>/<ticket>-<slug>` branch name, then creates and checks out that branch
- The `copilot` category is registered as a placeholder with no commands yet

## Capabilities

### New Capabilities

- `shell-screen-layout`: Updated Textual screen with header, help, activity/timeline, and command input zones
- `activity-log`: Persistent in-session log area that records command history, status messages, and execution events
- `command-categories`: Top-level category grouping for commands (`openspec`, `git`, `copilot`) surfaced in `help` output
- `openspec-branch-helper`: Headless helper that detects the latest OpenSpec change folder and creates a git branch named after it
- `git-branch-helper`: Headless helper that normalises free-text into a `<category>/<ticket>-<slug>` branch name and creates + checks out the branch

### Modified Capabilities

- `interactive-shell`: Help output and command routing updated to support categories and new commands
- `command-registry`: Gains support for grouping commands under a category label

## Impact

- `src/mdt/ui/shell_screen.py`: Layout restructured; activity log widget added
- `src/mdt/commands/`: New modules `openspec_branch.py`, `git_branch.py`, `copilot.py`; `__init__.py` updated to register all categories
- `src/mdt/commands/help.py`: Updated to render category-grouped output
- `src/mdt/core/registry.py`: Optional `category` field added to registered commands
- `tests/core/`: New test modules for the two branch helpers
- `pyproject.toml`: No new dependencies (uses `gitpython` or subprocess; textual already present)

