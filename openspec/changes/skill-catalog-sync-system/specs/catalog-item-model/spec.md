## MODIFIED Requirements

### Requirement: Catalog item data model with kind and classification
The `CatalogItem` data model SHALL represent a catalog item with fields: `name` (str), `kind` (one of instruction, prompt, skill, agent), `description` (str), `tags` (dict with optional keys: language, topic, domain — each a list of strings), `targets` (dict mapping install target name to target config), and `source` (dict with a `files` list of relative paths). For managed skills, each target config MAY also declare `consumers` (a list of logical consumer names) so one physical install path can serve multiple workflow consumers.

#### Scenario: Valid catalog item with all fields
- **WHEN** a `CatalogItem` is created with name="openspec-propose", kind="skill", tags={language: ["python"], topic: ["openspec"]}, targets={claude: {install_mode: "symlink", path_template: ".claude/skills/{name}/SKILL.md"}}, source={files: ["SKILL.md"]}
- **THEN** all fields are accessible and the item is valid

#### Scenario: Catalog item with no language tags
- **WHEN** a `CatalogItem` is created with tags={topic: ["testing"]} and no language key
- **THEN** the item is valid and `item.tags.get("language", [])` returns an empty list

#### Scenario: Managed skill target with shared consumers
- **WHEN** a `CatalogItem` is created with targets={shared_claude: {install_mode: "symlink", path_template: ".claude/skills/{name}/SKILL.md", consumers: ["claude", "copilot"]}}
- **THEN** the item preserves the physical install path template
- **AND** the target metadata preserves both logical consumers

### Requirement: Catalog item loaded from YAML
The system SHALL load a `CatalogItem` from a `catalog-item.yaml` file in the item's directory, including any optional target `consumers` metadata.

#### Scenario: Load from valid YAML
- **WHEN** a directory contains a `catalog-item.yaml` with valid fields
- **THEN** `CatalogItem.from_yaml(path)` returns a populated `CatalogItem` instance

#### Scenario: Load managed skill YAML with shared consumers
- **WHEN** a target entry in `catalog-item.yaml` contains `consumers: ["claude", "copilot"]`
- **THEN** `CatalogItem.from_yaml(path)` preserves that consumer list on the target config

#### Scenario: Load from missing YAML
- **WHEN** the specified path does not exist
- **THEN** `CatalogItem.from_yaml(path)` raises `FileNotFoundError`

### Requirement: Target config model
Each target entry in a `CatalogItem` SHALL have `install_mode` (one of "symlink", "copy", or "render") and `path_template` (a string with `{name}` placeholder). A target entry MAY additionally declare `consumers` to represent the logical consumers served by the same physical install definition.

#### Scenario: Target config with symlink mode
- **WHEN** a target config has install_mode="symlink" and path_template=".claude/skills/{name}/SKILL.md"
- **THEN** `target_config.install_mode` is "symlink" and `target_config.resolve_path("my-skill")` returns ".claude/skills/my-skill/SKILL.md"

#### Scenario: Target config with explicit consumers
- **WHEN** a target config includes `consumers=["claude", "copilot"]`
- **THEN** the target config preserves both logical consumers for status and install reporting

#### Scenario: Target config without explicit consumers
- **WHEN** a target config omits `consumers`
- **THEN** the system treats the target key itself as the default logical consumer for backward compatibility

