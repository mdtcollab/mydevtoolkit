## MODIFIED Requirements

### Requirement: Open catalog item in external editor
The `CatalogEditor` SHALL open the canonical central source file of a catalog item or managed skill reference in an external editor process, preferring the central source over any installed project copy.

#### Scenario: Editor from $EDITOR environment variable
- **WHEN** `editor.edit(item)` is called and `$EDITOR` is set to "vim"
- **THEN** a subprocess is launched with `vim <source_file_path>` attached to the terminal

#### Scenario: Fallback editor chain
- **WHEN** `$EDITOR` is not set
- **THEN** the system falls back to "nano", then "vi"

#### Scenario: Item with multiple source files opens primary file
- **WHEN** `editor.edit(item)` is called and the item has multiple source files
- **THEN** the first file in `source.files` is opened

#### Scenario: Managed skill edit prefers canonical source
- **WHEN** a managed skill is installed in the current project as a copy or symlink
- **AND** the user requests editing that skill through MDT
- **THEN** the editor opens the canonical central source file instead of the installed project copy

### Requirement: Resolve the canonical source path for editing
The `CatalogEditor` SHALL resolve the full filesystem path to the canonical source file from the catalog root and item metadata, and SHALL use that central path when a managed skill is referenced from the current project's manifest.

#### Scenario: Path resolution
- **WHEN** the catalog root is `/home/user/.config/mdt/catalog` and item name is "my-skill" with source file "SKILL.md"
- **THEN** the resolved path is `/home/user/.config/mdt/catalog/my-skill/source/SKILL.md`

#### Scenario: Managed manifest reference resolves to central path
- **WHEN** the current project manifest records `my-skill` as installed at `.claude/skills/my-skill/SKILL.md`
- **THEN** the editor resolves the edit path to `/home/user/.config/mdt/catalog/my-skill/source/SKILL.md`

