## ADDED Requirements

### Requirement: Discover all catalog items from catalog directory
The `CatalogRegistry` SHALL scan the catalog root directory and return a list of all `CatalogItem` instances found (one per subdirectory containing `catalog-item.yaml`).

#### Scenario: Catalog with multiple items
- **WHEN** the catalog root contains directories "skill-a" and "skill-b", each with a valid `catalog-item.yaml`
- **THEN** `registry.list_items()` returns two `CatalogItem` instances

#### Scenario: Empty catalog
- **WHEN** the catalog root directory exists but contains no item directories
- **THEN** `registry.list_items()` returns an empty list

#### Scenario: Catalog root does not exist
- **WHEN** the catalog root directory does not exist
- **THEN** `registry.list_items()` returns an empty list

### Requirement: Retrieve a single catalog item by name
The `CatalogRegistry` SHALL return a single `CatalogItem` by its name, or `None` if not found.

#### Scenario: Item exists
- **WHEN** `registry.get_item("openspec-propose")` is called and the item exists
- **THEN** a `CatalogItem` with `name="openspec-propose"` is returned

#### Scenario: Item not found
- **WHEN** `registry.get_item("nonexistent")` is called
- **THEN** `None` is returned

### Requirement: Filter catalog items by kind
The `CatalogRegistry` SHALL support filtering items by kind.

#### Scenario: Filter by kind=skill
- **WHEN** `registry.list_items(kind="skill")` is called and the catalog contains items of kinds skill, instruction, and agent
- **THEN** only items with kind="skill" are returned

### Requirement: Filter catalog items by tag
The `CatalogRegistry` SHALL support filtering items by tag category and value.

#### Scenario: Filter by language tag
- **WHEN** `registry.list_items(tag=("language", "python"))` is called
- **THEN** only items whose tags include language=["python", ...] are returned

### Requirement: Filter catalog items by target
The `CatalogRegistry` SHALL support filtering items by target compatibility.

#### Scenario: Filter by target=claude
- **WHEN** `registry.list_items(target="claude")` is called
- **THEN** only items that have a "claude" key in their targets dict are returned

### Requirement: Configurable catalog root path
The `CatalogRegistry` SHALL accept a catalog root path, defaulting to `~/.config/mdt/catalog/`. The path SHALL be overridable via `MDT_CATALOG_PATH` environment variable.

#### Scenario: Default path used
- **WHEN** `MDT_CATALOG_PATH` is not set
- **THEN** the registry uses `~/.config/mdt/catalog/`

#### Scenario: Custom path via environment
- **WHEN** `MDT_CATALOG_PATH` is set to `/tmp/my-catalog`
- **THEN** the registry uses `/tmp/my-catalog`

