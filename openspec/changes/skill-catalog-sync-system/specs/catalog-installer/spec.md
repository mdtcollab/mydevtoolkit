## MODIFIED Requirements

### Requirement: Install updates the project manifest
The `CatalogInstaller` SHALL record the installed item in the project manifest after a successful install, including the actual install mode used, the physical installed path, the logical consumers served by that install, and the hashes/timestamps needed for later status and sync checks.

#### Scenario: Manifest updated after managed skill install
- **WHEN** a managed skill is successfully installed
- **THEN** the project manifest contains an entry for the item with its name, kind, install target key, logical consumers, install mode, installed path, source hash, installed hash, and observed last-edited timestamps

#### Scenario: Symlink fallback records actual mode
- **WHEN** a managed skill requests `symlink` install mode
- **AND** the installer falls back to `copy`
- **THEN** the manifest records `copy` as the actual install mode used

## ADDED Requirements

### Requirement: Install supports shared physical targets for multiple logical consumers
The `CatalogInstaller` SHALL install a managed skill to the physical path defined by the selected install target and preserve any logical consumer list attached to that install target.

#### Scenario: Install to shared `.claude` target
- **WHEN** a managed skill target resolves to `.claude/skills/{name}/SKILL.md`
- **AND** that target declares logical consumers `claude` and `copilot`
- **THEN** the installer writes or links the skill at `.claude/skills/<name>/SKILL.md`
- **AND** the installation record preserves both logical consumers

### Requirement: Copied installs remain trackable for later sync
The `CatalogInstaller` SHALL record enough metadata for copied installs to be re-evaluated and re-installed later without losing auditability.

#### Scenario: Copy install records installed fingerprint
- **WHEN** a managed skill is installed using copy mode
- **THEN** the installer records the installed content fingerprint in the project manifest
- **AND** later status or sync operations can compare that fingerprint to the current project and central versions

### Requirement: Re-installing a managed skill replaces the tracked project copy
The `CatalogInstaller` SHALL support re-installing a previously managed copied skill by replacing the tracked project files and refreshing the manifest metadata.

#### Scenario: Sync re-installs out-of-date copied skill
- **WHEN** a copied managed skill in the project is classified as `central newer`
- **AND** a sync operation requests re-installation from the central catalog
- **THEN** the installer replaces the tracked project copy with the central version
- **AND** the project manifest is updated with the new hashes and timestamps

