## ADDED Requirements

### Requirement: Discover project skills from known locations
The `CatalogRegistry` SHALL discover project skills from known project locations without requiring those project installs to already exist as catalog items in the central MDT catalog.

#### Scenario: Discover `.github` and `.claude` project skills
- **WHEN** the current project contains `.github/skills/review-helper/SKILL.md`
- **AND** the current project contains `.claude/skills/release-helper/SKILL.md`
- **THEN** project skill discovery returns both skills as discovered entries
- **AND** discovery does not require a `catalog-item.yaml` file beside those project installs

#### Scenario: Project has no known skill locations
- **WHEN** the current project contains neither `.github/skills` nor `.claude/skills`
- **THEN** project skill discovery returns an empty result without error

### Requirement: Discovery preserves physical location and logical consumers
The `CatalogRegistry` SHALL preserve both the physical install path and the logical consumers implied by the discovered location for each managed skill candidate.

#### Scenario: `.claude` skill reports shared consumers
- **WHEN** a skill is discovered at `.claude/skills/review-helper/SKILL.md`
- **THEN** the discovery result records the physical path `.claude/skills/review-helper/SKILL.md`
- **AND** the discovery result records logical consumers `claude` and `copilot`

#### Scenario: `.github` skill reports Copilot consumer
- **WHEN** a skill is discovered at `.github/skills/review-helper/SKILL.md`
- **THEN** the discovery result records the physical path `.github/skills/review-helper/SKILL.md`
- **AND** the discovery result records logical consumer `copilot`

### Requirement: Registry correlates central and project versions of the same skill
The `CatalogRegistry` SHALL correlate a central catalog skill and a discovered project skill with the same managed name into a unified registry view that still preserves both source records.

#### Scenario: Central and project versions both exist
- **WHEN** the central catalog contains `review-helper`
- **AND** the current project contains `.claude/skills/review-helper/SKILL.md`
- **THEN** registry status includes one managed skill entry for `review-helper`
- **AND** that entry includes both the central source details and the project install details

#### Scenario: Skill exists only in the project
- **WHEN** the current project contains `.github/skills/local-helper/SKILL.md`
- **AND** the central catalog does not contain `local-helper`
- **THEN** registry status still includes `local-helper` as a discovered project-only skill candidate

