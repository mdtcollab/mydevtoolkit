## MODIFIED Requirements

### Requirement: Help command groups output by category
The `help` command SHALL list commands grouped under their category heading, with uncategorised commands shown under a "Built-in" heading. The `settings` category SHALL appear in the category list.

#### Scenario: Grouped help output
- **WHEN** the user submits `help`
- **THEN** the result message lists categories as headings including `settings` and their commands below each heading

#### Scenario: Empty categories are shown
- **WHEN** the registry declares a category with no registered commands
- **THEN** the help output still shows that category with a placeholder entry

