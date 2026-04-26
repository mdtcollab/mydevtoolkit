## MODIFIED Requirements

### Requirement: Load manifest from project
The `CatalogManifest` SHALL load installed item records from `.mdt/catalog.json` in the project root, preserve richer managed-skill metadata when present, and default missing managed-skill fields for older manifest records.

#### Scenario: Manifest exists with managed skill metadata
- **WHEN** `.mdt/catalog.json` exists with valid JSON including managed-skill metadata
- **THEN** `CatalogManifest.load(project_root)` returns a manifest with all recorded items and their managed-skill fields intact

#### Scenario: Manifest does not exist
- **WHEN** `.mdt/catalog.json` does not exist
- **THEN** `CatalogManifest.load(project_root)` returns an empty manifest

#### Scenario: Older manifest record omits new managed fields
- **WHEN** `.mdt/catalog.json` contains an older item record without logical consumers or installed hash fields
- **THEN** `CatalogManifest.load(project_root)` still succeeds
- **AND** the missing managed-skill fields are defaulted so status and sync logic can continue safely

### Requirement: Record an installed item
The `CatalogManifest` SHALL store an entry per installed item with name, kind, install target key, logical consumers, install mode, installed path, source hash, installed hash, central last edited timestamp, project last edited timestamp, and installed-at timestamp.

#### Scenario: Add a managed skill record
- **WHEN** `manifest.record_install(name="my-skill", kind="skill", install_target="shared_claude", logical_consumers=["claude", "copilot"], install_mode="symlink", installed_path=".claude/skills/my-skill/SKILL.md", source_hash="abc123", installed_hash="abc123", central_last_edited_at="2026-04-26T10:00:00+00:00", project_last_edited_at="2026-04-26T10:00:00+00:00")`
- **THEN** `manifest.get("my-skill")` returns the recorded entry with all managed-skill fields

## ADDED Requirements

### Requirement: Determine managed skill freshness state
The `CatalogManifest` SHALL classify each managed skill's current state as `in sync`, `project newer`, `central newer`, `symlinked`, or `missing` using stored install metadata plus current filesystem observations.

#### Scenario: In-sync copied install
- **WHEN** the current project content hash matches the current central source hash
- **THEN** the manifest classification for that skill is `in sync`

#### Scenario: Central catalog has changed since installation
- **WHEN** the current central source hash differs from the project's installed hash
- **AND** the project copy still matches the last installed hash
- **THEN** the manifest classification for that skill is `central newer`

#### Scenario: Project copy has changed since installation
- **WHEN** the project's installed hash differs from the last installed hash
- **AND** the current central source hash still matches the last installed hash
- **THEN** the manifest classification for that skill is `project newer`

#### Scenario: Installed path is a symlink to the canonical source
- **WHEN** the installed project path resolves to a symlink pointing at the canonical central source
- **THEN** the manifest classification for that skill is `symlinked`

#### Scenario: Installed files are missing
- **WHEN** a manifest record exists for a managed skill
- **AND** the installed project file or directory is no longer present
- **THEN** the manifest classification for that skill is `missing`

### Requirement: Expose last edited timestamps for status output
The `CatalogManifest` SHALL expose the current central and project last-edited timestamps for each managed skill so status output can explain freshness decisions.

#### Scenario: Status requests last-edited information
- **WHEN** a caller requests the status of a managed skill that exists in both the central catalog and the current project
- **THEN** the manifest returns both the central last-edited timestamp and the project last-edited timestamp with the status result

