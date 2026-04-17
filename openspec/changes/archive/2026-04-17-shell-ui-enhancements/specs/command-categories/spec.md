## ADDED Requirements

### Requirement: Commands can be registered with an optional category
The `CommandRegistry` SHALL accept an optional `category` parameter on `register()`. When provided, the command is associated with that category string.

#### Scenario: Registration with category
- **WHEN** `registry.register("openspec_branch", OpensspecBranchCommand, category="openspec")` is called
- **THEN** the command is resolvable by name and its category is stored

#### Scenario: Registration without category
- **WHEN** `registry.register("help", HelpCommand)` is called without a `category` argument
- **THEN** the command is registered with `category=None`

### Requirement: Registry exposes all registered commands with metadata
The `CommandRegistry` SHALL provide a method `all()` returning a list of `(name, handler_class, category)` tuples for all registered commands.

#### Scenario: all() returns category metadata
- **WHEN** `registry.all()` is called after registering commands with and without categories
- **THEN** each tuple contains the name, class, and category (or `None`) for that command

### Requirement: Help command groups output by category
The `help` command SHALL list commands grouped under their category heading, with uncategorised commands shown under a "General" or "Built-in" heading.

#### Scenario: Grouped help output
- **WHEN** the user submits `help`
- **THEN** the result message lists categories as headings and their commands below each heading

#### Scenario: Uncategorised commands shown under built-in heading
- **WHEN** the user submits `help` and some commands have no category
- **THEN** those commands appear under a "Built-in" heading

### Requirement: Two-word commands are routed via underscore key
The `CommandDispatcher` SHALL attempt to resolve `<verb>_<subverb>` when `<verb>` alone is unregistered and the input has at least two tokens.

#### Scenario: Two-word command dispatched
- **WHEN** the user submits `openspec branch`
- **THEN** the dispatcher resolves key `openspec_branch` and executes the matching handler

#### Scenario: Unknown two-word command returns error result
- **WHEN** the user submits `openspec unknown`
- **THEN** a `CommandResult` with `success=False` and an appropriate message is returned

