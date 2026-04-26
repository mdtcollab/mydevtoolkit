## ADDED Requirements

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
For projects detected as OpenSpec, the system SHALL infer workflow progress from OpenSpec change artifacts and report the current change name, likely last OpenSpec command, and next recommended OpenSpec command.

#### Scenario: Proposed change awaiting implementation
- **WHEN** the latest OpenSpec change has proposal/design/specs/tasks artifacts complete and implementation has not started
- **THEN** the result includes the current change name
- **AND** the result includes `last command: /opsx:propose`
- **AND** the result includes `next recommended command: /opsx:apply`

#### Scenario: Change already archived
- **WHEN** no active OpenSpec change directory exists for the latest change lifecycle
- **THEN** the result reports OpenSpec with command guidance aligned to starting a new change (for example `/opsx:propose`)

### Requirement: Spec Kit workflow status includes current iteration and command guidance
For projects detected as Spec Kit, the system SHALL infer workflow progress from Spec Kit iteration artifacts and report the current iteration name, likely last Spec Kit command, and next recommended Spec Kit command.

#### Scenario: Iteration planning complete and task breakdown pending
- **WHEN** Spec Kit artifacts indicate planning has completed for the active iteration but tasks are not yet generated
- **THEN** the result includes the current iteration name
- **AND** the result includes `last command: /speckit.plan`
- **AND** the result includes `next recommended command: /speckit.tasks`

#### Scenario: Iteration with no detected progress
- **WHEN** a Spec Kit iteration is detected but only initial scaffold artifacts are present
- **THEN** the command guidance recommends the earliest practical Spec Kit command for progressing the iteration

### Requirement: Workflow state inference lives in the headless core
Workflow detection and recommendation logic SHALL execute in the core layer and SHALL be independently testable without shell UI rendering.

#### Scenario: Command consumes core workflow state service
- **WHEN** `workflow status` is executed
- **THEN** the command handler delegates workflow detection and recommendation inference to a headless core helper/service
- **AND** unit tests can validate the helper/service behavior using project fixture directories

