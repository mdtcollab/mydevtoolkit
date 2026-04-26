## Why

`workflow status` can currently infer likely workflow progress from project artifacts, but it cannot reliably tell users which OpenSpec or Spec Kit command actually ran last. MDT needs a higher-confidence workflow history mechanism so the command can prefer tracked events when available and fall back to inference only when no tracked history exists.

## What Changes

- Add a headless workflow event tracking system that records normalized OpenSpec and Spec Kit command events.
- Add an MDT-owned workflow event ingestion surface that AI coding agent hooks or other integrations can call without depending on the UI shell.
- Extend workflow status reporting to prefer tracked history for `last command` while continuing to infer current change or iteration and next recommended command from project state.
- Surface provenance metadata for the reported last command so users can tell whether it came from tracked history or inference.
- Keep event persistence, normalization, query logic, and fallback resolution in the headless core.

## Capabilities

### New Capabilities
- `workflow-history`: Records, persists, and resolves normalized workflow command events for OpenSpec and Spec Kit projects.
- `workflow-event-ingestion`: Provides a stable MDT-owned ingestion surface that external AI coding agent hooks and other integrations can call to submit workflow events.
- `workflow-status-provenance`: Defines how workflow status uses tracked history for last-command reporting and exposes whether the result was tracked or inferred.

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `src/mdt/core/` for workflow event persistence, normalization, query logic, and workflow-status reconciliation
  - `src/mdt/commands/` for workflow event ingestion entrypoints and updated `workflow status` output
  - future integrations that emit OpenSpec and Spec Kit events into MDT
- Affected tests:
  - new tests for workflow event storage, validation, and lookup
  - updated workflow status tests for tracked-history preference, provenance reporting, and inference fallback
- No UI redesign required; the shell remains a presentation layer over headless core behavior.

