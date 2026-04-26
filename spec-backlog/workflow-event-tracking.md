## Why

`workflow status` currently infers the last OpenSpec or Spec Kit command from project artifacts. That works for rough workflow state, but it cannot reliably determine the actual last command because artifacts may be edited manually, produced outside MDT, or correspond to multiple possible command histories.

MDT needs a higher-confidence workflow history mechanism so `workflow status` can prefer tracked command events when available and fall back to inference only when necessary.

## What Changes

- Add a headless workflow event tracking system to MDT that records OpenSpec and Spec Kit command events.
- Add an MDT-owned event ingestion API/command that external AI coding agent hooks can call when workflow commands are executed.
- Update `workflow status` to prefer tracked command history for `last command` and use current project-state inference as fallback.
- Include metadata about the source of workflow history (for example `tracked-agent-hook` vs `inferred`).
- Keep event persistence and resolution logic in the headless core, independent of the UI shell.

## Capabilities

### New Capabilities
- `workflow-history`: Records and resolves workflow command events for OpenSpec and Spec Kit projects.
- `workflow-event-ingestion`: Accepts normalized workflow events from AI coding agent hooks or other integrations.

### Modified Capabilities
- `workflow-status-helper`: `workflow status` prefers tracked workflow history when available and labels inferred fallback results explicitly.

## Impact

- Affected code:
  - `src/mdt/core/` for workflow history persistence, normalization, and resolution
  - `src/mdt/commands/` for event ingestion command(s) and updated `workflow status`
- Affected tests:
  - new tests for event storage, history resolution, and fallback behavior
  - updated `workflow status` tests for tracked vs inferred last-command behavior
- No UI redesign required; shell remains the presentation layer

## Context

MDT already has a headless workflow detection helper that infers workflow type, current change/iteration, and likely command progression from filesystem artifacts. This is sufficient for recommendation logic but not reliable enough for historical facts like the last command that was actually run.

AI coding agents may expose hook systems that can emit workflow command events when slash-commands or workflow commands execute. MDT should be able to ingest those events without depending on a single agent runtime.

## Goals / Non-Goals

**Goals:**
- Add a headless workflow event history store owned by MDT.
- Accept workflow command events from external AI agent hooks through a stable MDT ingestion surface.
- Prefer tracked workflow history for `last command` in `workflow status`.
- Fall back to inference when no tracked history is available.
- Surface command-history source metadata such as `tracked-agent-hook` or `inferred`.

**Non-Goals:**
- Requiring a specific AI coding agent runtime.
- Replacing filesystem inference for current workflow state and next-command recommendation.
- Implementing full plugin SDKs for all agent environments in this change.

## Decisions

1. Introduce a normalized workflow event model in core.
   - Decision: store normalized events with fields such as workflow type, command id, raw command, timestamp, success flag, project identifier, current change/iteration, and source.
   - Rationale: allows one storage/query model regardless of whether events came from OpenSpec hooks, Spec Kit hooks, or other integrations.
   - Alternative considered: store raw strings only; rejected because it makes querying and reconciliation brittle.

2. Use MDT-owned persistence in the headless core.
   - Decision: persist workflow events in an MDT-managed local store rather than relying on the agent runtime to preserve history.
   - Rationale: keeps status resolution deterministic and testable from MDT alone.
   - Alternative considered: in-memory tracking only; rejected because it would be session-bound and fragile.

3. Expose event ingestion through an MDT command or equivalent stable entrypoint.
   - Decision: provide an ingestion surface that agent hooks can invoke with structured arguments or payloads.
   - Rationale: decouples MDT from specific hook implementations and makes integrations replaceable.
   - Alternative considered: direct file writes by external hooks; rejected because it couples external tools to MDT storage layout.

4. Keep workflow state resolution hybrid.
   - Decision: `workflow status` uses tracked history for `last command`, but continues to infer current change/iteration and next recommended command from project artifacts.
   - Rationale: tracked history is strongest for past events, while filesystem state is strongest for current project condition.
   - Alternative considered: derive everything from tracked history; rejected because users may change artifacts outside tracked command runs.

5. Surface history provenance explicitly.
   - Decision: include source metadata in the status result, distinguishing values such as `tracked-agent-hook`, `tracked-wrapper`, `inferred`, or `unknown`.
   - Rationale: makes status output more trustworthy and easier to debug.
   - Alternative considered: hide provenance; rejected because users cannot tell whether the result is factual or inferred.

## Risks / Trade-offs

- [Agent hook ecosystem variance] -> Mitigation: define one MDT ingestion contract and keep per-agent hookup outside the core design
- [History/state divergence] -> Mitigation: resolve current state from project artifacts and use tracking only for historical facts
- [Unbounded history growth] -> Mitigation: use a compact append-only format and bound retained event history if needed
- [Partial integrations] -> Mitigation: design graceful fallback to inference when no tracked history exists

## ADDED Requirements

### Requirement: MDT records normalized workflow command events
The system SHALL support recording normalized workflow command events for OpenSpec and Spec Kit workflows.

#### Scenario: Record OpenSpec event
- **WHEN** an integration submits an OpenSpec command event for the current project
- **THEN** MDT stores a normalized event containing the workflow type, command identifier, timestamp, success state, and project identifier

#### Scenario: Record Spec Kit event
- **WHEN** an integration submits a Spec Kit command event for the current project
- **THEN** MDT stores a normalized event containing the workflow type, command identifier, timestamp, success state, and project identifier

### Requirement: Workflow event ingestion is independent of UI rendering
Workflow event ingestion SHALL execute in the headless core and SHALL be invokable without the Textual shell UI.

#### Scenario: Agent hook calls ingestion surface
- **WHEN** an external AI coding agent hook invokes the MDT workflow event ingestion surface
- **THEN** MDT records the event without requiring shell UI state

### Requirement: Workflow status prefers tracked history for last command
When tracked workflow events are available for the current project context, `workflow status` SHALL prefer tracked history over filesystem inference for the reported last command.

#### Scenario: Tracked event available
- **WHEN** the workflow history contains a successful tracked command event relevant to the current project context
- **THEN** `workflow status` reports that tracked command as the last command

#### Scenario: No tracked event available
- **WHEN** the workflow history contains no relevant tracked event for the current project context
- **THEN** `workflow status` falls back to inferred last-command logic

### Requirement: Workflow status reports history provenance
The system SHALL expose whether the reported last command came from tracked history or inference.

#### Scenario: Tracked history source reported
- **WHEN** `workflow status` uses a tracked event
- **THEN** the result includes source metadata indicating tracked history

#### Scenario: Inferred history source reported
- **WHEN** `workflow status` falls back to artifact inference
- **THEN** the result includes source metadata indicating inference

## ADDED Requirements

### Requirement: MDT exposes a stable workflow event ingestion surface
The system SHALL provide a stable MDT-owned ingestion surface that external integrations can call to submit workflow command events.

#### Scenario: Valid ingestion request
- **WHEN** an integration submits a valid workflow event payload
- **THEN** MDT accepts and records the event

#### Scenario: Invalid ingestion request
- **WHEN** an integration submits an invalid or incomplete workflow event payload
- **THEN** MDT rejects the request with a clear validation error

### Requirement: Workflow events preserve command source information
The ingestion surface SHALL allow integrations to identify the source of the event, such as agent hook or wrapper integration.

#### Scenario: Agent hook source recorded
- **WHEN** an event is submitted with source `agent-hook`
- **THEN** MDT stores that source information with the event

## MODIFIED Requirements

### Requirement: workflow status command reports detected workflow type
The system SHALL provide a `workflow status` command that inspects project artifacts and reports one workflow detection outcome: `openspec`, `speckit`, `both`, or `none`.

#### Scenario: OpenSpec project detected
- **WHEN** a project contains OpenSpec workflow markers and does not contain Spec Kit markers
- **THEN** `workflow status` returns success with `workflow type: openspec`

#### Scenario: Spec Kit project detected
- **WHEN** a project contains Spec Kit workflow markers and does not contain OpenSpec markers
- **THEN** `workflow status` returns success with `workflow type: speckit`

#### Scenario: Both workflow systems detected
- **WHEN** a project contains both OpenSpec and Spec Kit markers
- **THEN** `workflow status` returns a predictable explicit result indicating both workflow systems are present
- **AND** the result does not silently choose one workflow system

#### Scenario: No supported workflow system detected
- **WHEN** a project contains neither OpenSpec nor Spec Kit markers
- **THEN** `workflow status` returns a clear message that no supported workflow system was found

### Requirement: OpenSpec workflow status includes current change and command guidance
For projects detected as OpenSpec, the system SHALL infer workflow progress from OpenSpec change artifacts and report the current change name, the last OpenSpec command, and the next recommended OpenSpec command.

#### Scenario: Tracked OpenSpec command available
- **WHEN** a relevant tracked OpenSpec command exists for the current project context
- **THEN** the result uses that tracked command as the reported last command
- **AND** the result marks the last-command source as tracked history

#### Scenario: No tracked OpenSpec command available
- **WHEN** no relevant tracked OpenSpec command exists for the current project context
- **THEN** the result infers the last command from OpenSpec artifacts
- **AND** the result marks the last-command source as inferred

### Requirement: Spec Kit workflow status includes current iteration and command guidance
For projects detected as Spec Kit, the system SHALL infer workflow progress from Spec Kit iteration artifacts and report the current iteration name, the last Spec Kit command, and the next recommended Spec Kit command.

#### Scenario: Tracked Spec Kit command available
- **WHEN** a relevant tracked Spec Kit command exists for the current project context
- **THEN** the result uses that tracked command as the reported last command
- **AND** the result marks the last-command source as tracked history

#### Scenario: No tracked Spec Kit command available
- **WHEN** no relevant tracked Spec Kit command exists for the current project context
- **THEN** the result infers the last command from Spec Kit artifacts
- **AND** the result marks the last-command source as inferred

