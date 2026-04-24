## ADDED Requirements

### Requirement: catalog_list command lists catalog items
The `catalog_list` command SHALL list all catalog items, displaying name, kind, and description. It SHALL support optional filters: `--kind`, `--language`, `--topic`, `--target`.

#### Scenario: List all items
- **WHEN** `catalog_list` is executed with no arguments
- **THEN** the result output contains all catalog items with name, kind, and description

#### Scenario: List filtered by kind
- **WHEN** `catalog_list --kind skill` is executed
- **THEN** only items with kind="skill" are shown

#### Scenario: Empty catalog
- **WHEN** `catalog_list` is executed and no catalog items exist
- **THEN** the result output indicates the catalog is empty

### Requirement: catalog_add command scaffolds a new catalog item
The `catalog_add` command SHALL create a new catalog item directory with a `catalog-item.yaml` and empty `source/` directory in the catalog root.

#### Scenario: Add a new skill
- **WHEN** `catalog_add my-skill --kind skill` is executed
- **THEN** a directory `my-skill/` is created in the catalog root with `catalog-item.yaml` and `source/` subdirectory

#### Scenario: Item already exists
- **WHEN** `catalog_add my-skill --kind skill` is executed and `my-skill` already exists
- **THEN** the result is a failure with an error message indicating the item already exists

### Requirement: catalog_install command installs an item into the project
The `catalog_install` command SHALL install a catalog item into the current project for a specified target.

#### Scenario: Install for Claude target
- **WHEN** `catalog_install my-skill --target claude` is executed
- **THEN** the item is installed into the project per the Claude target config and the manifest is updated

#### Scenario: Item not found
- **WHEN** `catalog_install nonexistent --target claude` is executed
- **THEN** the result is a failure with an error message

### Requirement: catalog_remove command removes an installed item
The `catalog_remove` command SHALL remove an installed catalog item's files from the project and update the manifest.

#### Scenario: Remove installed item
- **WHEN** `catalog_remove my-skill` is executed and the item is installed
- **THEN** the installed file(s) are deleted and the manifest entry is removed

#### Scenario: Item not installed
- **WHEN** `catalog_remove my-skill` is executed and the item is not installed
- **THEN** the result is a failure with an error message

### Requirement: catalog_sync command re-syncs installed items
The `catalog_sync` command SHALL check all installed items for drift and re-install any that have changed.

#### Scenario: No drift detected
- **WHEN** `catalog_sync` is executed and all installed items match their source
- **THEN** the result output indicates everything is up to date

#### Scenario: Drift detected and resolved
- **WHEN** `catalog_sync` is executed and one item's source has changed
- **THEN** the changed item is re-installed and the manifest is updated

### Requirement: catalog_edit command opens item in editor
The `catalog_edit` command SHALL open the canonical source file of a catalog item in an external editor.

#### Scenario: Edit existing item
- **WHEN** `catalog_edit my-skill` is executed
- **THEN** the editor is launched with the canonical source file path

#### Scenario: Item not found
- **WHEN** `catalog_edit nonexistent` is executed
- **THEN** the result is a failure with an error message

