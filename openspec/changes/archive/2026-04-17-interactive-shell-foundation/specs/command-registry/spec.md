## ADDED Requirements

### Requirement: Commands can be registered by name
The `CommandRegistry` SHALL allow associating a string command name with a handler class.

#### Scenario: Successful registration
- **WHEN** `registry.register("help", HelpCommand)` is called
- **THEN** `registry.resolve("help")` returns `HelpCommand`

#### Scenario: Duplicate registration raises an error
- **WHEN** `registry.register("help", HelpCommand)` is called a second time
- **THEN** the registry raises `ValueError`

### Requirement: Unknown command resolves to None
The `CommandRegistry` SHALL return `None` when asked to resolve an unregistered name.

#### Scenario: Unknown command
- **WHEN** `registry.resolve("unknown")` is called for a name that was never registered
- **THEN** the return value is `None`

### Requirement: Registry lists all registered command names
The `CommandRegistry` SHALL expose the set of all registered command names.

#### Scenario: List names
- **WHEN** `registry.names()` is called after registering `help` and `exit`
- **THEN** the returned collection contains exactly `{"help", "exit"}`

