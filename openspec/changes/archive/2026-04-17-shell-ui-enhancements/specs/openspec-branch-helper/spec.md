## ADDED Requirements

### Requirement: openspec branch detects the latest change folder
The `openspec_branch` helper SHALL scan `openspec/changes/` in the project root and select the subdirectory with the most recent modification time.

#### Scenario: Latest change folder selected
- **WHEN** `openspec/changes/` contains one or more subdirectories
- **THEN** the helper identifies the subdirectory with the highest mtime as the target change

#### Scenario: No changes folder returns error
- **WHEN** `openspec/changes/` does not exist or is empty
- **THEN** the helper returns a `CommandResult` with `success=False` and a descriptive message

### Requirement: openspec branch creates and checks out a git branch
The helper SHALL create a new git branch named after the detected change folder (with a `feature/` prefix if none is present) and check it out.

#### Scenario: Branch created from change name
- **WHEN** the latest change folder is named `shell-ui-enhancements`
- **THEN** the helper runs `git checkout -b feature/shell-ui-enhancements` and returns a successful `CommandResult`

#### Scenario: Branch creation failure returns error result
- **WHEN** `git checkout -b` fails (e.g., branch already exists)
- **THEN** the helper returns a `CommandResult` with `success=False` and the git error message

### Requirement: openspec branch reports the branch name in its result
The helper SHALL include the created branch name in the `CommandResult.output`.

#### Scenario: Result contains branch name
- **WHEN** the branch is successfully created
- **THEN** `CommandResult.output` contains the branch name

