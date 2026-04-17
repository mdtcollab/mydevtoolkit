## MODIFIED Requirements

### Requirement: Commands can be registered by name
The `CommandRegistry` SHALL allow associating a string command name with a handler class and an optional `category` string.

#### Scenario: Successful registration without category
- **WHEN** `registry.register("help", HelpCommand)` is called
- **THEN** `registry.resolve("help")` returns `HelpCommand`

#### Scenario: Successful registration with category
- **WHEN** `registry.register("openspec_branch", OpenspecBranchCommand, category="openspec")` is called
- **THEN** `registry.resolve("openspec_branch")` returns `OpenspecBranchCommand`

#### Scenario: Duplicate registration raises an error
- **WHEN** `registry.register("help", HelpCommand)` is called a second time
- **THEN** the registry raises `ValueError`

## ADDED Requirements

### Requirement: Registry exposes all commands with metadata via all()
The `CommandRegistry` SHALL provide `all()` returning a list of `(name, handler_class, category)` tuples, where `category` is `None` if not set.

#### Scenario: all() includes category metadata
- **WHEN** `registry.all()` is called after mixed registrations
- **THEN** each tuple correctly reflects the stored category or `None`

