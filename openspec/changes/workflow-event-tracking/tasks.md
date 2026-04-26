## 1. Core workflow history model and storage

- [x] 1.1 Add a core workflow event model with normalized fields for workflow type, command id, raw command, timestamp, success state, project identifier, context, and source
- [x] 1.2 Implement MDT-owned persistence for workflow events in `src/mdt/core/` using an append-only store suitable for repeated ingestion and lookup
- [x] 1.3 Implement validation and normalization logic for incoming workflow events
- [x] 1.4 Implement lookup logic that returns the latest relevant successful tracked event for the current project and workflow context

## 2. Workflow event ingestion surface

- [x] 2.1 Add an MDT-owned ingestion entrypoint that external AI coding agent hooks can call without depending on the Textual UI shell
- [x] 2.2 Validate ingestion inputs and return clear errors for invalid or incomplete workflow event payloads
- [x] 2.3 Preserve event source metadata such as `agent-hook` when recording ingested events

## 3. Workflow status integration

- [x] 3.1 Extend the workflow status core result model to include last-command provenance metadata
- [x] 3.2 Update workflow status resolution to prefer tracked history for `last command` and fall back to current inferred behavior when no relevant tracked event exists
- [x] 3.3 Preserve existing headless inference for workflow type, current change or iteration, and next recommended command even when tracked history is available
- [x] 3.4 Update command output to surface whether the reported last command was tracked or inferred

## 4. Tests

- [x] 4.1 Add unit tests for workflow event normalization, validation, persistence, and lookup behavior
- [x] 4.2 Add workflow status tests covering tracked OpenSpec history, tracked Spec Kit history, failed-event exclusion, and inferred fallback
- [x] 4.3 Add ingestion entrypoint tests for valid payloads, invalid payloads, and source metadata preservation

## 5. Documentation and verification

- [x] 5.1 Document the workflow event ingestion contract for external AI coding agent hooks or integration authors
- [x] 5.2 Run targeted tests for workflow history, ingestion, and workflow status resolution

