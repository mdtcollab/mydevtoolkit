## MODIFIED Requirements

### Requirement: Commands can be registered by name
The `CommandRegistry` SHALL allow associating a string command name with a handler class and an optional category string.

#### Scenario: Successful registration without category
- **WHEN** `registry.register("help", HelpCommand)` is called
- **THEN** `registry.resolve("help")` returns `HelpCommand`

#### Scenario: Successful registration with category
- **WHEN** `registry.register("openspec_branch", OpenspecBranchCommand, category="openspec")` is called
- **THEN** `registry.resolve("openspec_branch")` returns `OpenspecBranchCommand`

#### Scenario: Duplicate registration raises an error
- **WHEN** `registry.register("help", HelpCommand)` is called a second time
- **THEN** the registry raises `ValueError`

#### Scenario: Catalog commands registered under catalog category
- **WHEN** the command registry is built
- **THEN** commands `catalog_list`, `catalog_add`, `catalog_install`, `catalog_remove`, `catalog_sync`, and `catalog_edit` are registered under the "catalog" category

