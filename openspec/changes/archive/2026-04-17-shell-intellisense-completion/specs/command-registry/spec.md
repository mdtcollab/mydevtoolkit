## ADDED Requirements

### Requirement: Registry exposes completable tokens for a given input prefix
The `CommandRegistry` SHALL provide a method `get_completions(prefix: str) -> list[str]` that returns command names and category sub-commands matching the given prefix.

#### Scenario: Empty prefix returns all top-level tokens
- **WHEN** `registry.get_completions("")` is called
- **THEN** the returned list contains all registered command names and declared category names

#### Scenario: Prefix filters to matching commands
- **WHEN** `registry.get_completions("he")` is called and `help` is registered
- **THEN** the returned list contains `"help"`

#### Scenario: Category prefix returns sub-commands
- **WHEN** `registry.get_completions("git ")` is called and `git_branch` is registered under `git`
- **THEN** the returned list contains `"branch"`

### Requirement: Registry retrieves argument completions from command handler
The `CommandRegistry` SHALL provide a method to invoke a command handler's `get_completions` method (if present) for argument-level completion.

#### Scenario: Handler with get_completions method
- **WHEN** `registry.get_argument_completions("git_branch", 0, ["fe"])` is called and `GitBranchCommand` has `get_completions` returning `["feature"]`
- **THEN** the returned list is `["feature"]`

#### Scenario: Handler without get_completions method
- **WHEN** `registry.get_argument_completions("help", 0, [])` is called and `HelpCommand` lacks `get_completions`
- **THEN** the returned list is empty

### Requirement: Commands may declare known argument completions
Command handler classes MAY implement a `get_completions(position: int, tokens: list[str]) -> list[str]` class method or static method that returns valid argument values for the given position.

#### Scenario: GitBranchCommand declares category completions
- **WHEN** `GitBranchCommand.get_completions(0, [])` is called
- **THEN** it returns the list of known category prefixes (`["bugfix", "chore", "feature", "hotfix", "refactor"]`)

#### Scenario: Command with no known completions
- **WHEN** a command does not implement `get_completions`
- **THEN** the registry returns an empty list for that command's argument completions

