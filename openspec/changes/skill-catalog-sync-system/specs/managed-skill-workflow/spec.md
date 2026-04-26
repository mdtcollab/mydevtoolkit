## ADDED Requirements

### Requirement: Discover managed skills from central and project locations
The system SHALL discover managed skills from the MDT central catalog and from known skill locations in the current project, including `.github/skills` and `.claude/skills`.

#### Scenario: Discover skills across central and project locations
- **WHEN** the central catalog contains `review-helper`
- **AND** the current project contains `.github/skills/review-helper/SKILL.md` and `.claude/skills/release-helper/SKILL.md`
- **THEN** discovery returns managed skill entries for both `review-helper` and `release-helper`
- **AND** each discovered entry identifies whether central content, project content, or both are present

#### Scenario: Known project locations are absent
- **WHEN** the current project does not contain `.github/skills` or `.claude/skills`
- **THEN** project skill discovery succeeds without error
- **AND** the project discovery result is empty

### Requirement: Import selected project skills into the central catalog with guided naming
The system SHALL support importing selected discovered project skills into the central MDT catalog and SHALL offer guided rename handling, including an explicit option to add an `mdt-` prefix to the imported skill name.

#### Scenario: Import selected skill with rename and prefix
- **WHEN** a user selects project skill `review-helper` for import
- **AND** the user chooses imported name `mdt-review-helper`
- **THEN** MDT creates or updates the canonical central skill entry under that imported name
- **AND** the imported record preserves the discovered source content and install metadata needed for later status and sync operations

#### Scenario: OpenSpec and SpecKit skills remain visible but are deselected by default
- **WHEN** project discovery finds skills whose names or metadata indicate OpenSpec or SpecKit workflows
- **THEN** those skills appear in the import selection results
- **AND** each such skill is marked as not selected by default
- **AND** other discovered skills continue to use the normal default selection behavior

### Requirement: Managed skill status uses reliable freshness comparison
The system SHALL determine managed skill freshness using canonical content comparison and install metadata, and SHALL report whether each managed skill is `in sync`, `project newer`, `central newer`, `symlinked`, or `missing`.

#### Scenario: Copied project skill is in sync with central catalog
- **WHEN** a managed skill is installed as a copied file in the project
- **AND** the project content fingerprint matches the central content fingerprint
- **THEN** status reports the skill as `in sync`

#### Scenario: Project copy is newer than central catalog
- **WHEN** a managed skill is installed as a copied file in the project
- **AND** the project content fingerprint differs from the central content fingerprint
- **AND** the project copy reflects user edits after installation
- **THEN** status reports the skill as `project newer`

#### Scenario: Central catalog is newer than project copy
- **WHEN** a managed skill is installed as a copied file in the project
- **AND** the central content fingerprint differs from the project content fingerprint
- **AND** the central catalog version reflects edits after installation
- **THEN** status reports the skill as `central newer`

#### Scenario: Skill is installed by symlink
- **WHEN** a managed skill's installed project path is a symlink to the canonical central source
- **THEN** status reports the skill as `symlinked`

#### Scenario: Managed skill is missing from the project
- **WHEN** the project manifest records a managed skill installation
- **AND** the installed project file or directory no longer exists
- **THEN** status reports the skill as `missing`

### Requirement: Managed skill status exposes install and edit context
The system SHALL expose each managed skill's physical install location, logical consumers, and last-edited information for both the project and central catalog so users can make auditable sync decisions.

#### Scenario: Shared `.claude` install reports logical consumers
- **WHEN** a managed skill is installed at `.claude/skills/review-helper/SKILL.md`
- **AND** that install serves both Claude and Copilot in MDT's metadata
- **THEN** status reports the physical install path as `.claude/skills/review-helper/SKILL.md`
- **AND** status reports the logical consumers as `claude` and `copilot`

#### Scenario: Last-edited information is shown for both sides
- **WHEN** MDT evaluates a managed skill that exists in both the central catalog and the current project
- **THEN** the status payload includes the last edited timestamp for the central version
- **AND** the status payload includes the last edited timestamp for the project version

