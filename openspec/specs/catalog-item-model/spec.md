## ADDED Requirements

### Requirement: Catalog item data model with kind and classification
The `CatalogItem` data model SHALL represent a catalog item with fields: `name` (str), `kind` (one of instruction, prompt, skill, agent), `description` (str), `tags` (dict with optional keys: language, topic, domain — each a list of strings), `targets` (dict mapping target name to target config), and `source` (dict with a `files` list of relative paths).

#### Scenario: Valid catalog item with all fields
- **WHEN** a `CatalogItem` is created with name="openspec-propose", kind="skill", tags={language: ["python"], topic: ["openspec"]}, targets={claude: {install_mode: "symlink", path_template: ".claude/skills/{name}/SKILL.md"}}, source={files: ["SKILL.md"]}
- **THEN** all fields are accessible and the item is valid

#### Scenario: Catalog item with no language tags
- **WHEN** a `CatalogItem` is created with tags={topic: ["testing"]} and no language key
- **THEN** the item is valid and `item.tags.get("language", [])` returns an empty list

### Requirement: Catalog item loaded from YAML
The system SHALL load a `CatalogItem` from a `catalog-item.yaml` file in the item's directory.

#### Scenario: Load from valid YAML
- **WHEN** a directory contains a `catalog-item.yaml` with valid fields
- **THEN** `CatalogItem.from_yaml(path)` returns a populated `CatalogItem` instance

#### Scenario: Load from missing YAML
- **WHEN** the specified path does not exist
- **THEN** `CatalogItem.from_yaml(path)` raises `FileNotFoundError`

### Requirement: Target config model
Each target entry in a `CatalogItem` SHALL have `install_mode` (one of "symlink", "copy", "render") and `path_template` (a string with `{name}` placeholder).

#### Scenario: Target config with symlink mode
- **WHEN** a target config has install_mode="symlink" and path_template=".claude/skills/{name}/SKILL.md"
- **THEN** `target_config.install_mode` is "symlink" and `target_config.resolve_path("my-skill")` returns ".claude/skills/my-skill/SKILL.md"

