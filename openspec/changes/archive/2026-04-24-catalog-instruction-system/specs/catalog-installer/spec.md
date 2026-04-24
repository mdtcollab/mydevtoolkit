## ADDED Requirements

### Requirement: Install a catalog item into a project via symlink
The `CatalogInstaller` SHALL create a symlink from the project target path to the canonical source file when the install mode is "symlink".

#### Scenario: Symlink install succeeds
- **WHEN** `installer.install(item, target="claude", project_root=path)` is called with install_mode="symlink"
- **THEN** a symlink is created at the resolved project path pointing to the canonical source file

#### Scenario: Symlink install creates parent directories
- **WHEN** the target path's parent directory does not exist
- **THEN** the installer creates the necessary parent directories before creating the symlink

### Requirement: Install a catalog item via copy
The `CatalogInstaller` SHALL copy the canonical source file to the project target path when the install mode is "copy".

#### Scenario: Copy install succeeds
- **WHEN** `installer.install(item, target="copilot", project_root=path)` is called with install_mode="copy"
- **THEN** the source file content is copied to the resolved project path

### Requirement: Install a catalog item via render
The `CatalogInstaller` SHALL render the canonical source through a target-specific renderer and write the output to the project target path when the install mode is "render".

#### Scenario: Render install succeeds
- **WHEN** `installer.install(item, target="opencode", project_root=path)` is called with install_mode="render"
- **THEN** the rendered content is written to the resolved project path

### Requirement: Fallback from symlink to copy when symlink is not feasible
The `CatalogInstaller` SHALL detect when symlink creation would fail (e.g., cross-filesystem) and fall back to copy mode automatically.

#### Scenario: Cross-filesystem fallback
- **WHEN** symlink creation raises `OSError` due to cross-filesystem
- **THEN** the installer falls back to copy mode and succeeds

### Requirement: Target not supported raises error
The `CatalogInstaller` SHALL raise `ValueError` when asked to install for a target that the catalog item does not support.

#### Scenario: Unsupported target
- **WHEN** `installer.install(item, target="unsupported", project_root=path)` is called and the item has no "unsupported" target config
- **THEN** a `ValueError` is raised

### Requirement: Install updates the project manifest
The `CatalogInstaller` SHALL record the installed item in the project manifest after a successful install.

#### Scenario: Manifest updated after install
- **WHEN** a catalog item is successfully installed
- **THEN** the project manifest contains an entry for the item with its name, kind, target, install mode, installed path, and source hash

### Requirement: Install multiple source files
The `CatalogInstaller` SHALL install all source files listed in the catalog item's source.files list, not just a single file.

#### Scenario: Item with multiple source files
- **WHEN** a catalog item has source.files=["SKILL.md", "helpers.py"] and install_mode="copy"
- **THEN** both files are copied to the project under the target path directory

