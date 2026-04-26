## ADDED Requirements

### Requirement: Workflow status prefers tracked history for last command
When tracked workflow events are available for the current project context, `workflow status` SHALL prefer tracked history over filesystem inference for the reported last command.

#### Scenario: Tracked OpenSpec event available
- **WHEN** tracked workflow history contains a successful OpenSpec command event relevant to the current project context
- **THEN** `workflow status` reports that tracked command as the last command instead of an inferred OpenSpec command

#### Scenario: Tracked Spec Kit event available
- **WHEN** tracked workflow history contains a successful Spec Kit command event relevant to the current project context
- **THEN** `workflow status` reports that tracked command as the last command instead of an inferred Spec Kit command

#### Scenario: No tracked event available
- **WHEN** tracked workflow history contains no relevant successful event for the current project context
- **THEN** `workflow status` falls back to inferred last-command logic

### Requirement: Workflow status reports last-command provenance
The system SHALL expose whether the reported last command came from tracked history or inference.

#### Scenario: Tracked history source reported
- **WHEN** `workflow status` uses a tracked event
- **THEN** the result includes source metadata indicating tracked history

#### Scenario: Inferred history source reported
- **WHEN** `workflow status` falls back to artifact inference
- **THEN** the result includes source metadata indicating inference

### Requirement: Workflow status keeps state and recommendation inference in core
The system SHALL continue to infer workflow type, current change or iteration, and next recommended command from headless core project-state logic even when tracked history is available for the last command.

#### Scenario: Tracked last command with inferred next step
- **WHEN** `workflow status` finds a tracked last command for the active workflow context
- **THEN** the command still uses current project artifacts to determine the current change or iteration and the next recommended command

