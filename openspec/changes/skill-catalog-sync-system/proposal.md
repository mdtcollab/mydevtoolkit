## Why

MDT already has a central catalog and basic install/sync commands, but skill management is still too manual for real project workflows. Users need MDT to discover reusable skills in both the current project and the central config catalog, import selected project skills into the canonical catalog, install or update managed skills back into a project, and clearly show which copy is newer without relying on ad hoc file copying.

## What Changes

- Extend catalog discovery so MDT can scan both the central MDT catalog and known project skill locations, including `.github/skills` and `.claude/skills`.
- Add a managed-skill workflow for importing discovered project skills into the central catalog, with guided rename support and an optional `mdt-` prefix during import.
- Keep OpenSpec-related and SpecKit-related skills visible during import/sync discovery, but deselect them by default so users do not promote them accidentally.
- Add project install and sync flows for selected central skills, supporting tracked copy and symlink modes and preferring symlinks when safe.
- Expand project manifest and comparison logic so MDT can report whether the project version is newer, the central version is newer, the skill is in sync, symlinked, missing, or otherwise out of date.
- Expose managed-skill status and edit flows so users can inspect freshness, last-edited timestamps, install mode, logical consumers, and open the canonical central version in an external editor by default.

## Capabilities

### New Capabilities
- `managed-skill-workflow`: Discover, import, install, compare, and sync managed skills between the current project and MDT's central catalog with predictable status reporting.

### Modified Capabilities
- `catalog-item-model`: Represent managed skill install metadata with both physical install locations and logical consumer targets so shared `.claude` installs remain explicit.
- `catalog-registry`: Expand discovery to known project skill locations and central skill locations, including `.claude` as a shared practical install target, while preserving physical install path and logical consumer metadata.
- `catalog-manifest`: Record per-project managed-skill metadata needed for freshness comparison, install tracking, and auditable sync decisions.
- `catalog-installer`: Support tracked installation and re-installation of selected central skills into the current project using symlink or copy modes.
- `catalog-commands`: Add user-facing import, install, status, sync, and selection behavior for managed skills, including default deselection rules for OpenSpec and SpecKit skills.
- `catalog-editor`: Default managed-skill editing to the canonical central source rather than an installed project copy.

## Impact

- Affected code:
  - `src/mdt/catalog/` for discovery, manifest/state modeling, comparison logic, install/update orchestration, and editor resolution
  - `src/mdt/commands/` for new or expanded catalog commands covering import, install, sync, status, and edit flows
  - shell command registration/help/completion wiring for new catalog workflows
- Affected tests:
  - new and updated tests under `tests/core/` for skill discovery, selection defaults, import/install behavior, freshness comparison, and manifest metadata
  - command-level tests covering import prompts/options, status output, sync decisions, and edit targeting
- No external services are required; the feature is filesystem- and metadata-driven and remains shell-first.


