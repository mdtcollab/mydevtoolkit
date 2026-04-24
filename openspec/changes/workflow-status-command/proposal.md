## Why

MDT currently has OpenSpec-focused helpers but no single command that tells users where they are in a spec workflow. Teams using either OpenSpec or Spec Kit need a consistent way to inspect current workflow state and get an actionable next step without manual guessing.

## What Changes

- Add a new workflow-oriented shell command exposed as `workflow status`.
- Detect whether the current project uses OpenSpec, Spec Kit, both, or neither using project artifacts instead of UI-only signals.
- For OpenSpec projects, infer the current change, likely last workflow command, and next recommended workflow command from change artifacts.
- For Spec Kit projects, infer the current iteration/state, likely last workflow command, and next recommended workflow command from Spec Kit artifacts.
- Return explicit, predictable results for unsupported (`none`) and ambiguous (`both`) detection states.
- Keep workflow detection and recommendation logic in headless core modules so behavior is testable and reusable by the shell UI.

## Capabilities

### New Capabilities
- `workflow-status-helper`: Detects OpenSpec or Spec Kit workflow state and returns actionable status metadata for the `workflow status` command.

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `src/mdt/commands/` (new command entrypoint for `workflow status`)
  - `src/mdt/core/` (workflow detection/state inference helpers)
  - command registration wiring used by shell dispatch
- Affected tests:
  - new and/or updated tests under `tests/core/` for detection, inference, and recommendations
  - command-level tests for output and edge cases (both/none detected)
- No external service dependencies expected; filesystem/project-state inspection only.

