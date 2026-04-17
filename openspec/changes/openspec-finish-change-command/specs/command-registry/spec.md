## MODIFIED Requirements

### Requirement: Commands can be registered by name
The `CommandRegistry` SHALL allow associating a string command name with a handler class and an optional category string.

#### Scenario: Successful registration without category
- **WHEN** `registry.register("help", HelpCommand)` is called
- **THEN** `registry.resolve("help")` returns `HelpCommand`

#### Scenario: Successful registration with category
- **WHEN** `registry.register("openspec_branch", OpenspecBranchCommand, category="openspec")` is called
- **THEN** `registry.resolve("openspec_branch")` returns `OpenspecBranchCommand`

#### Scenario: Registration of openspec_finish under openspec category
- **WHEN** `registry.register("openspec_finish", OpenspecFinishCommand, category="openspec")` is called
- **THEN** `registry.resolve("openspec_finish")` returns `OpenspecFinishCommand`

#### Scenario: Duplicate registration raises an error
- **WHEN** `registry.register("help", HelpCommand)` is called a second time
- **THEN** the registry raises `ValueError`

