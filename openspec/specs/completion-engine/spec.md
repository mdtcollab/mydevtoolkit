# completion-engine Specification

## Purpose
Define how the completion engine generates IntelliSense-style suggestions from the command registry.

## Requirements
### Requirement: CompletionEngine generates command completions from registry
The `CompletionEngine` SHALL accept the current input text and return a list of completion candidates by querying the `CommandRegistry` for commands and sub-commands that match the input prefix.

#### Scenario: Empty input returns all top-level commands
- **WHEN** the input is empty
- **THEN** the engine returns all registered command names and category prefixes as candidates

#### Scenario: Partial command prefix filters candidates
- **WHEN** the input is `"he"`
- **THEN** the engine returns `["help"]` (assuming `help` is registered)

#### Scenario: Category prefix followed by space lists sub-commands
- **WHEN** the input is `"git "` and `git_branch` is registered under category `git`
- **THEN** the engine returns `["branch"]` as the sub-command candidate

#### Scenario: No matches returns empty list
- **WHEN** the input is `"xyz"` and no command starts with `xyz`
- **THEN** the engine returns an empty list

### Requirement: CompletionEngine supports argument completion for commands with declared completions
The `CompletionEngine` SHALL invoke a command's `get_completions` method (if present) to retrieve valid argument tokens when the user is past the command/sub-command tokens.

#### Scenario: Command declares known argument values
- **WHEN** the input is `"git branch fe"` and `GitBranchCommand.get_completions(0, ["fe"])` returns `["feature"]`
- **THEN** the engine returns `["feature"]`

#### Scenario: Command does not declare completions
- **WHEN** the input is `"help "` and `HelpCommand` has no `get_completions` method
- **THEN** the engine returns an empty list for argument position

### Requirement: CompletionEngine is case-insensitive
The `CompletionEngine` SHALL perform case-insensitive prefix matching for commands, sub-commands, and argument tokens.

#### Scenario: Mixed-case input matches lowercase command
- **WHEN** the input is `"HE"`
- **THEN** the engine returns `["help"]`

### Requirement: CompletionEngine returns completions in sorted order
The `CompletionEngine` SHALL return completion candidates in alphabetical order.

#### Scenario: Multiple matches are sorted
- **WHEN** the input is `""`
- **THEN** the returned candidates are sorted alphabetically (e.g., `["exit", "git", "help", "openspec"]`)

