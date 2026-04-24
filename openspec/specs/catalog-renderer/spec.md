## ADDED Requirements

### Requirement: Render content for a target
The `CatalogRenderer` SHALL transform canonical source content into target-specific format for a given target name.

#### Scenario: Passthrough render for compatible target
- **WHEN** `renderer.render(content, source_path, target="claude")` is called and Claude's format matches the source
- **THEN** the original content is returned unchanged

#### Scenario: Transform render for differing target
- **WHEN** `renderer.render(content, source_path, target="opencode")` is called and OpenCode requires a different format
- **THEN** the content is transformed according to the OpenCode rendering rules

### Requirement: Register target-specific render functions
The `CatalogRenderer` SHALL support registering custom render functions per target name.

#### Scenario: Custom renderer registered
- **WHEN** a render function is registered for target "opencode"
- **THEN** `renderer.render(content, source_path, target="opencode")` uses that function

#### Scenario: No renderer registered falls back to passthrough
- **WHEN** no render function is registered for a target
- **THEN** `renderer.render(content, source_path, target)` returns the original content unchanged

### Requirement: Renderer receives source metadata
The render function SHALL receive the source content (str), source file path, and the catalog item metadata so it can make informed transformations.

#### Scenario: Render function receives item metadata
- **WHEN** a render function is called
- **THEN** it receives content, source_path, and item metadata as arguments

