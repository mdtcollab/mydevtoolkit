## ADDED Requirements

### Requirement: MDT exposes a stable workflow event ingestion surface
The system SHALL provide a stable MDT-owned ingestion surface that external integrations can call to submit workflow command events.

#### Scenario: Valid ingestion request
- **WHEN** an integration submits a valid workflow event payload
- **THEN** MDT accepts and records the event

#### Scenario: Invalid ingestion request
- **WHEN** an integration submits an invalid or incomplete workflow event payload
- **THEN** MDT rejects the request with a clear validation error

### Requirement: Workflow event ingestion is independent of UI rendering
Workflow event ingestion SHALL execute in the headless core and SHALL be invokable without the Textual shell UI.

#### Scenario: Agent hook calls ingestion surface
- **WHEN** an external AI coding agent hook invokes the MDT workflow event ingestion surface
- **THEN** MDT records the event without requiring shell UI state

### Requirement: Workflow events preserve command source information
The ingestion surface SHALL allow integrations to identify the source of the event, such as agent hook or wrapper integration.

#### Scenario: Agent hook source recorded
- **WHEN** an event is submitted with source `agent-hook`
- **THEN** MDT stores that source information with the event

