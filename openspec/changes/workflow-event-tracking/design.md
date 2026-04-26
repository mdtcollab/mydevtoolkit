## Context

MDT already has headless workflow detection that infers workflow type, current change or iteration, and likely next command from project artifacts. That inference is useful for current state, but it is not a reliable record of what command actually ran last, especially when users edit artifacts manually or invoke OpenSpec and Spec Kit workflows outside MDT.

This change adds a workflow history layer that can ingest events from external AI coding agent hooks while preserving the shell-first architecture. The implementation must remain useful even when no hook integration is installed, so tracked history needs to complement rather than replace filesystem inference.

## Goals / Non-Goals

**Goals:**
- Add a normalized workflow event model and persistence owned by MDT core.
- Provide a stable ingestion surface that external agent hooks can call without depending on Textual UI state.
- Prefer tracked history for `last command` in `workflow status` when relevant events exist.
- Preserve current artifact-based inference for workflow type, current change or iteration, and next recommended command.
- Expose provenance metadata so status results explain whether the last command is tracked or inferred.

**Non-Goals:**
- Requiring any single AI coding agent, IDE, or hook runtime.
- Replacing workflow-state inference entirely with event history.
- Shipping full per-agent hook installers in this change.

## Decisions

1. Use a normalized workflow event record in core.
   - Decision: define a core event model with fields such as workflow type, command identifier, raw command, timestamp, success flag, project identifier, current change or iteration, and event source.
   - Rationale: a single normalized shape allows event ingestion, validation, persistence, and lookup to work consistently for OpenSpec and Spec Kit.
   - Alternative considered: record raw command strings only; rejected because it weakens validation and makes context-aware lookup brittle.

2. Persist workflow history in an MDT-managed append-only local store.
   - Decision: store events in MDT-controlled persistence rather than relying on the agent runtime to remember history.
   - Rationale: persistence must outlive a shell session and stay available even if the event producer changes.
   - Alternative considered: in-memory tracking only; rejected because `workflow status` would lose historical accuracy across sessions.

3. Expose ingestion through an MDT-owned stable entrypoint.
   - Decision: provide an ingestion command or equivalent entrypoint that validates structured input and records events through headless core logic.
   - Rationale: this keeps external AI agent hooks decoupled from MDT's internal storage layout.
   - Alternative considered: let hooks write directly into the history file; rejected because it couples external integrations to MDT internals and increases corruption risk.

4. Resolve workflow status with tracked-history preference plus inferred fallback.
   - Decision: `workflow status` uses tracked history only for the reported last command and its provenance, while current change or iteration and next recommended command continue to come from project-state inference.
   - Rationale: historical facts and current project state are different concerns, and each has a stronger data source.
   - Alternative considered: derive all status fields from tracked history; rejected because users may edit or advance the project outside tracked commands.

5. Prefer relevant successful events over generic latest events.
   - Decision: history lookup should favor the latest successful event for the current project and active workflow context, using change or iteration metadata when available.
   - Rationale: this reduces false matches when several workflows or abandoned changes exist in one repository.
   - Alternative considered: always use the chronologically latest event; rejected because it can report unrelated or failed commands.

## Risks / Trade-offs

- [Agent hook ecosystems vary by runtime] -> Mitigation: define one MDT ingestion contract and keep hook-specific setup outside the core design.
- [Tracked history may drift from current artifacts] -> Mitigation: use tracked history only for last-command reporting and continue inferring current state from the filesystem.
- [History can grow unbounded over time] -> Mitigation: use a compact append-only format and reserve pruning or retention controls for a follow-up if growth becomes material.
- [Integrations may submit malformed or partial events] -> Mitigation: validate required fields at ingestion time and reject invalid payloads with clear errors.
- [Multiple active workflow-related changes may overlap during development] -> Mitigation: keep provenance and history requirements scoped to this change so implementation can build on the existing in-progress workflow status helper without redefining its base detection behavior.

## Migration Plan

- Introduce workflow history storage and ingestion as additive capabilities.
- Update `workflow status` to read tracked history first for last-command reporting while retaining current inference code as fallback.
- Leave existing repositories functional without any external hook setup; they continue to receive inferred results until tracked events exist.

## Open Questions

- Where should MDT persist workflow history by default: repository-local state or user-local state keyed by project path?
- Should the first ingestion surface accept structured CLI arguments, JSON input, or both?
- Should failed commands be stored for diagnostics while still excluding them from default `last command` reporting?

