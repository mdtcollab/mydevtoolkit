# activity-log Specification

## Purpose
Define the persistent in-session timeline of submitted commands and command outcomes.

## Requirements
### Requirement: Activity log accumulates entries for the session
The activity log widget SHALL append a new entry for each command submitted and each result received, persisting until the shell session ends.

#### Scenario: Entry added on command submission
- **WHEN** the user submits a command
- **THEN** the activity log shows a new entry with the command text

#### Scenario: Entry added on command result
- **WHEN** a command completes
- **THEN** the activity log appends the result message below the command entry

### Requirement: Activity log auto-scrolls to latest entry
The activity log SHALL scroll to the most recent entry automatically after each append.

#### Scenario: Auto-scroll on new entry
- **WHEN** a new entry is appended
- **THEN** the activity log scrolls so the new entry is visible without user interaction

### Requirement: Activity log is read-only
The activity log SHALL NOT accept keyboard input or editing.

#### Scenario: Click does not give editable focus
- **WHEN** the user clicks on the activity log
- **THEN** keyboard focus does not move to the log and the log content cannot be edited

