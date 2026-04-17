## ADDED Requirements

### Requirement: Repository root detection
On startup the system SHALL detect the nearest ancestor directory containing a `.git` folder as the repository root.

#### Scenario: Inside a git repository
- **WHEN** `mdt` is launched from a directory that is inside a git repository
- **THEN** `ProjectContext.repo_root` is set to the path of the directory containing `.git`

#### Scenario: Outside any git repository
- **WHEN** `mdt` is launched from a directory with no `.git` ancestor
- **THEN** `ProjectContext.repo_root` is `None` and the shell still starts successfully

### Requirement: Project name derived from repository root
The system SHALL derive `ProjectContext.project_name` from the basename of `repo_root`.

#### Scenario: Project name available
- **WHEN** a repo root is detected
- **THEN** `ProjectContext.project_name` equals the basename of the repo root directory

#### Scenario: No repo root
- **WHEN** no repo root is detected
- **THEN** `ProjectContext.project_name` is `None`

### Requirement: Current working directory captured
`ProjectContext.cwd` SHALL be set to the working directory at the time `mdt` was launched.

#### Scenario: CWD captured
- **WHEN** `mdt` is launched
- **THEN** `ProjectContext.cwd` equals the process working directory at launch time

### Requirement: Context available to all commands
The `ProjectContext` instance SHALL be injected into every command handler at dispatch time.

#### Scenario: Command receives context
- **WHEN** a command is dispatched
- **THEN** the command handler receives the current `ProjectContext` as a parameter

