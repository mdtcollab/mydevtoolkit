## 1. Managed skill data model and persistence

- [x] 1.1 Extend `src/mdt/catalog/item.py` to support shared install targets with explicit logical consumers while remaining backward compatible with existing catalog item YAML
- [x] 1.2 Extend `src/mdt/catalog/manifest.py` to load/save richer managed-skill records, including install target key, logical consumers, installed fingerprint, and central/project last-edited timestamps
- [x] 1.3 Add or update tests covering backward-compatible manifest loading and managed-skill item parsing

## 2. Discovery and status services

- [x] 2.1 Add headless discovery logic under `src/mdt/catalog/` or `src/mdt/core/` that scans the central catalog plus known project skill locations (`.github/skills` and `.claude/skills`)
- [x] 2.2 Implement correlation logic that combines central and project versions of the same skill into one managed-skill status view with physical path and logical consumer metadata
- [x] 2.3 Implement reliable freshness comparison using content fingerprints, symlink detection, and last-edited visibility for `in sync`, `project newer`, `central newer`, `symlinked`, and `missing` states
- [x] 2.4 Add focused tests for discovery, shared `.claude` consumer handling, and per-state freshness classification

## 3. Project-to-central import workflow

- [x] 3.1 Add import planning logic that converts discovered project skills into canonical central catalog entries without requiring pre-existing `catalog-item.yaml` files in the project
- [x] 3.2 Implement guided rename handling, including an explicit `mdt-` prefix option during import
- [x] 3.3 Implement deterministic default-selection rules that keep OpenSpec- and SpecKit-related skills visible but deselected by default
- [x] 3.4 Add tests covering import creation, rename/prefix behavior, and default selection heuristics

## 4. Install, sync, and edit integration

- [x] 4.1 Extend `src/mdt/catalog/installer.py` to preserve managed install metadata for both copy and symlink installs, including shared physical targets and actual mode used
- [x] 4.2 Update sync orchestration so copied skills are re-installed only when the central version is newer, while `project newer`, `symlinked`, and `missing` states are reported explicitly
- [x] 4.3 Ensure managed-skill editing resolves to the canonical central source path by default, even when invoked from a project installation context
- [x] 4.4 Add or update tests for installer metadata recording, sync decisions, and canonical edit targeting

## 5. Shell command workflows

- [x] 5.1 Add a `catalog import` command for project-to-central skill import and register it in the shell command registry/help/completion system
- [x] 5.2 Add a `catalog status` command that reports managed skill state, install mode, physical path, logical consumers, and last-edited information for the current project
- [x] 5.3 Extend `catalog install`, `catalog sync`, and `catalog edit` command handlers to use the new managed-skill services and metadata model
- [x] 5.4 Update command-level tests for import, install, status, sync, edit, and completion/help output

## 6. Verification

- [x] 6.1 Run targeted test files for catalog item parsing, manifest persistence, discovery/status logic, installer behavior, and catalog command handlers
- [x] 6.2 Perform a manual shell pass in a representative project fixture to verify project discovery, central import, install, status, sync, and edit flows
- [x] 6.3 Confirm copied and symlinked installs both remain auditable and that OpenSpec/SpecKit skills are shown but deselected by default during import

