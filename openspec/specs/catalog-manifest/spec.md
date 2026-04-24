## ADDED Requirements

### Requirement: Load manifest from project
The `CatalogManifest` SHALL load installed item records from `.mdt/catalog.json` in the project root.

#### Scenario: Manifest exists
- **WHEN** `.mdt/catalog.json` exists with valid JSON
- **THEN** `CatalogManifest.load(project_root)` returns a manifest with all recorded items

#### Scenario: Manifest does not exist
- **WHEN** `.mdt/catalog.json` does not exist
- **THEN** `CatalogManifest.load(project_root)` returns an empty manifest

### Requirement: Save manifest to project
The `CatalogManifest` SHALL persist its records to `.mdt/catalog.json`, creating the `.mdt/` directory if needed.

#### Scenario: Save creates directory and file
- **WHEN** `manifest.save(project_root)` is called and `.mdt/` does not exist
- **THEN** the directory is created and `catalog.json` is written

### Requirement: Record an installed item
The `CatalogManifest` SHALL store an entry per installed item with name, kind, target, install_mode, installed_path, source_hash, and installed_at timestamp.

#### Scenario: Add a record
- **WHEN** `manifest.record_install(name="my-skill", kind="skill", target="claude", install_mode="symlink", installed_path=".claude/skills/my-skill/SKILL.md", source_hash="abc123")`
- **THEN** `manifest.get("my-skill")` returns the recorded entry with all fields

### Requirement: Remove an installed item record
The `CatalogManifest` SHALL support removing a record by item name.

#### Scenario: Remove existing record
- **WHEN** `manifest.remove("my-skill")` is called for an existing record
- **THEN** `manifest.get("my-skill")` returns `None`

#### Scenario: Remove nonexistent record
- **WHEN** `manifest.remove("nonexistent")` is called
- **THEN** no error is raised

### Requirement: Detect drift between installed files and source
The `CatalogManifest` SHALL compare the stored source_hash against the current source hash to detect if the canonical source has changed since install.

#### Scenario: Source unchanged
- **WHEN** the current source hash matches the stored source_hash
- **THEN** `manifest.check_drift("my-skill", current_hash)` returns `False`

#### Scenario: Source changed
- **WHEN** the current source hash differs from the stored source_hash
- **THEN** `manifest.check_drift("my-skill", current_hash)` returns `True`

### Requirement: List all installed items
The `CatalogManifest` SHALL return a list of all installed item records.

#### Scenario: Multiple installed items
- **WHEN** the manifest contains three recorded items
- **THEN** `manifest.list_installed()` returns three records

