## ADDED Requirements

### Requirement: MDT records normalized workflow command events
The system SHALL support recording normalized workflow command events for OpenSpec and Spec Kit workflows.

#### Scenario: Record OpenSpec event
- **WHEN** an integration submits an OpenSpec command event for the current project
- **THEN** MDT stores a normalized event containing the workflow type, command identifier, timestamp, success state, and project identifier

#### Scenario: Record Spec Kit event
- **WHEN** an integration submits a Spec Kit command event for the current project
- **THEN** MDT stores a normalized event containing the workflow type, command identifier, timestamp, success state, and project identifier

### Requirement: Workflow history lookup prefers relevant successful events
The system SHALL resolve the last tracked workflow command by selecting the latest successful event relevant to the current project context.

#### Scenario: Matching event found for active OpenSpec change
- **WHEN** workflow history contains multiple OpenSpec events for a project
- **AND** one event matches the active change context and is the most recent successful matching event
- **THEN** MDT returns that event as the tracked last command for status reporting

#### Scenario: Failed event newer than last successful event
- **WHEN** a failed workflow event is newer than the last successful relevant event
- **THEN** MDT does not replace the reported tracked last command with the failed event

