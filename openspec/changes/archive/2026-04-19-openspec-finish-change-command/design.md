## Context

The mdt interactive shell has an OpenSpec-driven workflow for creating changes (`openspec branch`) but no guided command to finish a change branch and merge it back into the target branch. Developers must manually switch branches, pull, merge, and clean up — with no validation of OpenSpec lifecycle state. The `openspec_branch` command already establishes the pattern of deriving branch names from change folder names using known prefixes.

## Goals / Non-Goals

**Goals:**
- Provide a safe, guided "finish change" command that merges the current change branch back into `main`
- Enforce OpenSpec lifecycle: block merging if the change folder hasn't been archived
- Validate preconditions (clean working tree, valid branch, target branch exists)
- Handle merge conflicts gracefully without crashing the shell
- Optionally clean up the local change branch after successful merge

**Non-Goals:**
- Remote branch deletion or push operations
- Supporting arbitrary merge strategies or rebase workflows
- Implementing a full git merge UI
- Handling non-OpenSpec branches (the command validates the branch is change-related)

## Decisions

### 1. Derive change name from current branch name
The command will parse the current git branch (e.g., `feature/my-change-name`) to extract the change name (`my-change-name`), reusing the same prefix/name convention as `openspec_branch`. This avoids requiring the user to pass the change name as an argument.

**Alternative**: Require the change name as an argument — rejected because it adds friction and the branch name already encodes this information.

### 2. Block on unarchived change folder
If `openspec/changes/<change-name>/` exists, the command returns a failure result instructing the user to run `opsx:archive` first. This enforces the archive-before-merge lifecycle without automating the archive step (which may require user decisions).

**Alternative**: Auto-archive before merging — rejected because archiving may need user review and confirmation.

### 3. Use subprocess for all git operations
Consistent with `openspec_branch` and `git_branch`, all git operations (checkout, pull, merge, branch -d) use `subprocess.run` with `capture_output=True`. Errors are surfaced via `CommandResult` with `success=False`.

### 4. Default target branch to `main`
The target branch defaults to `main`. The command does not accept arguments to change this in the initial implementation, keeping the interface simple.

**Alternative**: Accept target branch as argument — can be added later if needed.

### 5. Command structure follows existing patterns
`OpenspecFinishCommand` follows the same class structure as `OpenspecBranchCommand`: a class with `__init__(registry)` and `__call__(args, context) -> CommandResult`, with core logic in a standalone function for testability.

## Risks / Trade-offs

- [Merge conflicts] → The command will detect merge conflicts and return a clear error with instructions, but will not resolve them automatically. The user must resolve manually and re-run or complete the merge by hand.
- [Branch name parsing] → If the branch name doesn't follow the expected `prefix/change-name` pattern, the command will report an error. This is acceptable since `openspec branch` creates branches in this format.
- [Target branch not up-to-date] → The command will `git pull` on the target branch before merging. If pull fails (e.g., no remote configured), it will warn but continue with the local state.

