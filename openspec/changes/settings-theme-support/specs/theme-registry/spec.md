## ADDED Requirements

### Requirement: Theme data model has four color fields
A `Theme` SHALL be a named tuple with fields: `name` (str), `primary` (str), `secondary` (str), `accent` (str), `surface` (str).

#### Scenario: Theme fields are accessible
- **WHEN** a `Theme` is created with `name="ocean"`, `primary="#a0c4ff"`, `secondary="#bdb2ff"`, `accent="#caffbf"`, `surface="#ffd6a5"`
- **THEN** `theme.name` returns `"ocean"` and all four color fields are accessible by name

### Requirement: At least five built-in themes are available
The `ThemeRegistry` SHALL contain at least 5 predefined themes, each with exactly 4 pastel color values that are visually cohesive and distinct from other themes.

#### Scenario: Listing built-in themes
- **WHEN** `ThemeRegistry.list_themes()` is called
- **THEN** the result contains at least 5 `Theme` objects with unique names

### Requirement: Themes can be looked up by name
The `ThemeRegistry` SHALL provide a `get_theme(name)` method returning the matching `Theme` or `None`.

#### Scenario: Known theme lookup
- **WHEN** `ThemeRegistry.get_theme("ocean")` is called for a registered theme
- **THEN** the matching `Theme` object is returned

#### Scenario: Unknown theme lookup
- **WHEN** `ThemeRegistry.get_theme("nonexistent")` is called
- **THEN** `None` is returned

### Requirement: Active theme can be get and set
The module SHALL expose `get_active_theme()` and `set_active_theme(name)`. The default active theme SHALL be the first built-in theme.

#### Scenario: Default active theme
- **WHEN** `get_active_theme()` is called without prior `set_active_theme`
- **THEN** a valid `Theme` is returned (the default)

#### Scenario: Setting active theme
- **WHEN** `set_active_theme("sunset")` is called with a valid theme name
- **THEN** `get_active_theme().name` returns `"sunset"`

#### Scenario: Setting unknown theme raises error
- **WHEN** `set_active_theme("nonexistent")` is called
- **THEN** a `ValueError` is raised

