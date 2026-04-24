## ADDED Requirements

### Requirement: Open catalog item in external editor
The `CatalogEditor` SHALL open the canonical source file of a catalog item in an external editor process.

#### Scenario: Editor from $EDITOR environment variable
- **WHEN** `editor.edit(item)` is called and `$EDITOR` is set to "vim"
- **THEN** a subprocess is launched with `vim <source_file_path>` attached to the terminal

#### Scenario: Fallback editor chain
- **WHEN** `$EDITOR` is not set
- **THEN** the system falls back to "nano", then "vi"

#### Scenario: Item with multiple source files opens primary file
- **WHEN** `editor.edit(item)` is called and the item has multiple source files
- **THEN** the first file in `source.files` is opened

### Requirement: Resolve the canonical source path for editing
The `CatalogEditor` SHALL resolve the full filesystem path to the canonical source file from the catalog root and item metadata.

#### Scenario: Path resolution
- **WHEN** the catalog root is `/home/user/.config/mdt/catalog` and item name is "my-skill" with source file "SKILL.md"
- **THEN** the resolved path is `/home/user/.config/mdt/catalog/my-skill/source/SKILL.md`

### Requirement: Editor not found raises error
The `CatalogEditor` SHALL raise a descriptive error if no editor can be found.

#### Scenario: No editor available
- **WHEN** `$EDITOR` is not set and neither "nano" nor "vi" is available on the system
- **THEN** a `RuntimeError` is raised with a message indicating no editor was found

