## MODIFIED Requirements

### Requirement: catalog_install command installs an item into the project
The `catalog_install` command SHALL install one or more selected catalog skills from the central catalog into the current project using the requested install target, and SHALL support copy and symlink modes where the selected install target allows them.

#### Scenario: Install selected skill to shared `.claude` target
- **WHEN** `catalog_install review-helper --target shared_claude` is executed
- **THEN** the skill is installed into the current project at the shared `.claude` target path
- **AND** the project manifest is updated with the managed install metadata

#### Scenario: Item not found
- **WHEN** `catalog_install nonexistent --target shared_claude` is executed
- **THEN** the result is a failure with an error message

### Requirement: catalog_sync command re-syncs installed items
The `catalog_sync` command SHALL evaluate all managed skills installed in the current project and SHALL update copied project installs whose central catalog version is newer, while reporting non-updatable states such as `project newer`, `symlinked`, or `missing` explicitly.

#### Scenario: No updates required
- **WHEN** `catalog_sync` is executed and all managed skills are `in sync` or `symlinked`
- **THEN** the result output indicates everything is up to date

#### Scenario: Central version is newer and copied install is updated
- **WHEN** `catalog_sync` is executed and one copied managed skill is classified as `central newer`
- **THEN** that skill is re-installed from the central catalog
- **AND** the manifest is updated

#### Scenario: Project version is newer
- **WHEN** `catalog_sync` is executed and one copied managed skill is classified as `project newer`
- **THEN** the command does not overwrite the project copy silently
- **AND** the result output reports that the project version is newer

### Requirement: catalog_edit command opens item in editor
The `catalog_edit` command SHALL open the canonical central source file of a managed catalog skill in an external editor, even when the request is made from the current project's managed installation context.

#### Scenario: Edit existing managed skill
- **WHEN** `catalog_edit my-skill` is executed for a managed skill present in the central catalog
- **THEN** the editor is launched with the canonical central source file path

#### Scenario: Edit managed skill installed in project
- **WHEN** `catalog_edit my-skill` is executed and the skill is installed in the current project as a copy or symlink
- **THEN** the editor still opens the canonical central source file rather than the installed project copy

#### Scenario: Item not found
- **WHEN** `catalog_edit nonexistent` is executed
- **THEN** the result is a failure with an error message

## ADDED Requirements

### Requirement: catalog_import command imports project skills into the central catalog
The `catalog_import` command SHALL discover skills from known locations in the current project, show the discovered skills with explicit default selections, and import the user-selected skills into the MDT central catalog.

#### Scenario: Import selected project skill with guided prefix option
- **WHEN** `catalog_import` is executed and the user selects `review-helper`
- **AND** the user accepts the guided `mdt-` prefix option
- **THEN** MDT imports the skill into the central catalog as `mdt-review-helper`

#### Scenario: OpenSpec and SpecKit skills are deselected by default
- **WHEN** `catalog_import` discovery finds OpenSpec-related or SpecKit-related skills
- **THEN** those skills are displayed in the import selection results
- **AND** those skills are marked deselected by default

### Requirement: catalog_status command shows managed skill freshness for the current project
The `catalog_status` command SHALL display the managed skills known for the current project and report each skill's freshness state, install mode, physical install path, logical consumers, and last-edited timestamps.

#### Scenario: Status shows project and central freshness
- **WHEN** `catalog_status` is executed in a project with managed skills
- **THEN** the output includes each skill's state such as `in sync`, `project newer`, `central newer`, `symlinked`, or `missing`
- **AND** the output includes the project and central last-edited information for each skill

