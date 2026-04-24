## Why

The OpenSpec workflow currently supports creating changes and branching (`openspec branch`), but lacks a guided command to finish a change branch and merge it back into `main`. Developers must manually handle validation, archiving, and merging — risking forgotten archives, dirty merges, or orphaned branches. A dedicated "finish change" command completes the OpenSpec branch lifecycle with safety checks.

## What Changes

- Add a new `openspec_finish` command under the `openspec` category that safely finishes the current change branch
- The command validates the current branch is an OpenSpec change branch, checks for unarchived change folders, ensures a clean working tree, and performs a guided merge back into the target branch (defaulting to `main`)
- If the related OpenSpec change folder still exists, the command blocks and instructs the user to archive first via `opsx:archive`
- After a successful merge, the command optionally offers local branch cleanup

## Capabilities

### New Capabilities
- `openspec-finish-helper`: Define the OpenSpec finish-change workflow command that validates, archives-checks, and merges a change branch back into the target branch

### Modified Capabilities
- `command-registry`: The registry gains a new `openspec_finish` command registered under the `openspec` category

## Impact

- New file: `src/mdt/commands/openspec_finish.py`
- Modified file: `src/mdt/commands/__init__.py` (register new command)
- New spec: `openspec/specs/openspec-finish-helper/spec.md`
- New test: `tests/core/test_openspec_finish_command.py`
- Git operations: checkout, pull, merge, branch deletion — all via subprocess

