## 1. Core workflow detection and inference

- [x] 1.1 Add a new core module (for example `src/mdt/core/workflow_status.py`) with workflow detection that classifies a project as `openspec`, `speckit`, `both`, or `none` from filesystem markers
- [x] 1.2 Implement OpenSpec state inference that derives current change name, likely last `/opsx:*` command, and next recommended `/opsx:*` command from active change artifacts
- [x] 1.3 Implement Spec Kit state inference that derives current iteration name, likely last `/speckit.*` command, and next recommended `/speckit.*` command from iteration artifacts
- [x] 1.4 Define a normalized result payload structure in core for command consumption and test assertions

## 2. Command integration

- [x] 2.1 Create `src/mdt/commands/workflow_status.py` with `WorkflowStatusCommand` that delegates all detection/inference logic to the core helper
- [x] 2.2 Format command output to include workflow type, current change/iteration, last command, and next recommended command when available
- [x] 2.3 Handle `both` and `none` detection states with explicit, predictable messages and no silent workflow selection

## 3. Registration and shell discoverability

- [x] 3.1 Register `workflow_status` in `src/mdt/commands/__init__.py` under a `workflow` category so users can run `workflow status`
- [x] 3.2 Verify command-dispatch and completion behavior for two-word routing and category suggestions remains correct

## 4. Tests

- [x] 4.1 Add core tests (for example `tests/core/test_workflow_status.py`) for detection outcomes: openspec-only, speckit-only, both, and none
- [x] 4.2 Add inference tests for OpenSpec artifact progression and Spec Kit iteration progression to validate last/next command recommendations
- [x] 4.3 Add command-level tests (for example `tests/core/test_workflow_status_command.py`) that validate user-facing output for success, ambiguous, and unsupported cases

## 5. Verification

- [x] 5.1 Run targeted test files for workflow status and related command registry/dispatcher behavior
- [x] 5.2 Perform a quick manual shell check that `workflow status` reports expected fields in a representative project fixture

