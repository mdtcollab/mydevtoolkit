## Context

MDT already supports workflow-specific helper commands (for example OpenSpec helpers), but users still need to inspect project files manually to understand current workflow state. This change introduces a workflow-agnostic status command while preserving MDT's shell-first architecture and keeping decision logic in headless core code.

Key constraints:
- Detection must be based on project structure and artifacts, not user-provided mode flags.
- Detection must handle `openspec`, `speckit`, `both`, and `none` explicitly.
- Recommendations must be practical and derived from observed state rather than a static message.

## Goals / Non-Goals

**Goals:**
- Add a `workflow status` command that reports workflow type and current state.
- Introduce testable core helpers for workflow detection and state inference.
- Infer the most likely last workflow command and next recommended command for OpenSpec and Spec Kit.
- Return predictable, clear messages for ambiguous (`both`) and unsupported (`none`) projects.

**Non-Goals:**
- Implementing full OpenSpec or Spec Kit execution flows.
- Adding new OpenSpec CLI wrappers beyond status inspection.
- Supporting arbitrary third workflow systems in this change.

## Decisions

1. Add a dedicated headless workflow status helper in core.
   - Decision: create core functions that inspect filesystem artifacts and return a normalized workflow status payload consumed by a command handler.
   - Rationale: keeps logic reusable and testable without shell rendering coupling.
   - Alternative considered: implement logic directly in command class; rejected because it mixes orchestration and domain inference.

2. Use deterministic detection precedence with explicit conflict outcomes.
   - Decision: detect OpenSpec markers and Spec Kit markers independently, then resolve into one of: `openspec`, `speckit`, `both`, `none`.
   - Rationale: prevents silent misclassification and satisfies predictable behavior requirements.
   - Alternative considered: always prefer OpenSpec if both are present; rejected because it hides ambiguity.

3. Infer OpenSpec state from change artifact progression.
   - Decision: evaluate active change directory and presence/completion of `proposal.md`, `design.md`, `tasks.md`, and spec files to infer likely last and next `/opsx:*` command.
   - Rationale: aligns recommendations with OpenSpec artifact lifecycle instead of static guidance.
   - Alternative considered: infer from git history/branch names only; rejected as too weak when users edit artifacts directly.

4. Infer Spec Kit state from iteration and generated artifact progression.
   - Decision: inspect Spec Kit iteration folders and expected artifacts to estimate current iteration, likely last `/speckit.*` command, and next recommended command.
   - Rationale: mirrors OpenSpec approach and supports headless test fixtures.
   - Alternative considered: require a Spec Kit state file; rejected because repositories may only contain generated artifacts.

5. Register as a two-word command key `workflow_status` under a `workflow` category.
   - Decision: use existing multi-word dispatch (`workflow status` -> `workflow_status`) and help/completion category support.
   - Rationale: preserves existing shell command architecture and keeps command discoverable.
   - Alternative considered: single command name `workflow_status`; rejected because user-facing command should remain natural language.

## Risks / Trade-offs

- [Spec Kit structure variance] -> Mitigation: define a minimal required marker set and fail with explicit unsupported/ambiguous messages when markers are incomplete.
- [Heuristic drift as workflows evolve] -> Mitigation: centralize inference rules in one module and cover with fixture-like unit tests.
- [False confidence in inferred last command] -> Mitigation: frame output as likely command based on artifacts and keep recommendation actionable even when history is uncertain.
- [Dual-system repositories during migration] -> Mitigation: treat as `both` and avoid auto-selecting one workflow.

