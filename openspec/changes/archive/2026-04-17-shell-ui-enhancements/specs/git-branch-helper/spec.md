## ADDED Requirements

### Requirement: git branch normalises free-text into a branch name
The `git_branch` helper SHALL parse free-text arguments into a `<category>/<ticket>-<slug>` branch name according to the following rules:
- The category prefix MUST be one of: `feature`, `bugfix`, `hotfix`, `chore`, `refactor`
- The ticket number MUST match `[a-z]+-[0-9]+` (lowercase letters, hyphen, digits)
- Remaining tokens form the slug (lowercased, joined with hyphens)
- Category, ticket, and at least one slug token are all required

#### Scenario: Valid free-text normalised
- **WHEN** the user submits `git branch feature abc-123 login system`
- **THEN** the helper produces branch name `feature/abc-123-login-system`

#### Scenario: Missing category returns error
- **WHEN** the free-text does not contain a recognised category prefix
- **THEN** the helper returns a `CommandResult` with `success=False` describing the missing category

#### Scenario: Missing ticket returns error
- **WHEN** the free-text does not contain a token matching `[a-z]+-[0-9]+`
- **THEN** the helper returns a `CommandResult` with `success=False` describing the missing ticket

#### Scenario: Ticket is normalised to lowercase
- **WHEN** the ticket token is provided as `ABC-123`
- **THEN** the normalised branch name uses `abc-123`

### Requirement: git branch creates and checks out the normalised branch
The helper SHALL execute `git checkout -b <normalised-name>` and return a `CommandResult` indicating success or failure.

#### Scenario: Branch created successfully
- **WHEN** normalisation succeeds and `git checkout -b` exits with code 0
- **THEN** the helper returns a `CommandResult` with `success=True` and the branch name in `output`

#### Scenario: git failure propagated as error result
- **WHEN** `git checkout -b` exits with a non-zero code
- **THEN** the helper returns a `CommandResult` with `success=False` and stderr in the message

