# openspec-finish-helper Specification

## Purpose
Define the OpenSpec helper that finishes a change branch by validating lifecycle state and merging it back into the target branch.

## Requirements
### Requirement: openspec finish detects the change name from the current branch
The `openspec_finish` helper SHALL parse the current git branch name to extract the OpenSpec change name, stripping known prefixes (`feature/`, `bugfix/`, `hotfix/`, `chore/`, `refactor/`).

#### Scenario: Branch with feature prefix
- **WHEN** the current branch is `feature/my-change-name`
- **THEN** the extracted change name is `my-change-name`

#### Scenario: Branch with no recognized prefix
- **WHEN** the current branch is `main` or has no recognized prefix
- **THEN** the command returns a `CommandResult` with `success=False` and a message indicating the branch is not an OpenSpec change branch

### Requirement: openspec finish blocks if the change folder still exists
The `openspec_finish` helper SHALL check whether `openspec/changes/<change-name>/` exists. If it does, the command SHALL return a failure result instructing the user to archive the change first.

#### Scenario: Change folder still present
- **WHEN** the change folder `openspec/changes/my-change-name/` exists
- **THEN** the command returns `success=False` with a message instructing the user to run `opsx:archive` first

#### Scenario: Change folder already archived or absent
- **WHEN** the change folder `openspec/changes/my-change-name/` does not exist
- **THEN** the command proceeds with the merge workflow

### Requirement: openspec finish requires a clean working tree
The `openspec_finish` helper SHALL verify the git working tree is clean before proceeding. If there are uncommitted changes, it SHALL return a failure result.

#### Scenario: Dirty working tree
- **WHEN** the working tree has uncommitted changes
- **THEN** the command returns `success=False` with a message about uncommitted changes

#### Scenario: Clean working tree
- **WHEN** the working tree is clean
- **THEN** the command proceeds to the next step

### Requirement: openspec finish switches to the target branch and updates it
The `openspec_finish` helper SHALL switch to the target branch (defaulting to `main`) and attempt to pull the latest changes.

#### Scenario: Successful switch and pull
- **WHEN** `git checkout main` and `git pull` both succeed
- **THEN** the command proceeds to merge

#### Scenario: Target branch does not exist
- **WHEN** `git checkout main` fails because the branch does not exist
- **THEN** the command returns `success=False` with a descriptive error

#### Scenario: Pull fails but checkout succeeded
- **WHEN** `git checkout main` succeeds but `git pull` fails
- **THEN** the command continues with the local state (warning included in output)

### Requirement: openspec finish merges the change branch into the target
The `openspec_finish` helper SHALL merge the change branch into the target branch using `git merge --no-ff`.

#### Scenario: Successful merge
- **WHEN** `git merge --no-ff feature/my-change-name` succeeds
- **THEN** the command returns `success=True` with a message confirming the merge

#### Scenario: Merge conflict
- **WHEN** `git merge --no-ff feature/my-change-name` fails due to conflicts
- **THEN** the command aborts the merge with `git merge --abort` and returns `success=False` with a message describing the conflict and instructing the user to resolve manually

### Requirement: openspec finish reports the merge result with branch details
The `openspec_finish` helper SHALL include the source and target branch names in the `CommandResult`.

#### Scenario: Result contains branch details
- **WHEN** the merge is successful
- **THEN** `CommandResult.output` contains both the source branch name and target branch name
- **AND** `CommandResult.data` contains `source_branch` and `target_branch` keys

