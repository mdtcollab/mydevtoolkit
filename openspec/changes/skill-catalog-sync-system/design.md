## Context

MDT already has the foundations of a reusable catalog system: canonical items live under the MDT config directory, install operations can copy or symlink catalog content into a project, and the project manifest records a minimal installation record. What is missing is a first-class skill-management workflow that treats project skills and central skills as two synchronized views of the same managed asset.

This change is cross-cutting because it touches discovery, metadata modeling, install/update orchestration, project manifests, command UX, and editor targeting. It must also preserve MDT's shell-first interaction model and keep filesystem/business rules in headless modules rather than UI code.

Key constraints:
- The MDT config area remains the canonical central catalog location.
- Known project skill locations include both `.github/skills` and `.claude/skills`, and `.claude` may represent a shared practical install location for more than one logical consumer.
- OpenSpec- and SpecKit-related skills must remain visible in discovery results but be deselected by default for project-to-central promotion.
- Freshness decisions must use durable comparison signals such as content fingerprints and symlink state, not only wall-clock timestamps.
- Editing a managed skill from the shell should open the canonical central source by default.

## Goals / Non-Goals

**Goals:**
- Add a headless managed-skill workflow that can discover skills in the current project and in the central catalog.
- Support importing selected project skills into the central catalog with guided rename and optional `mdt-` prefix handling.
- Support installing selected central skills into the current project and updating them later while preserving trackable install metadata.
- Report clear per-skill states such as `in sync`, `project newer`, `central newer`, `symlinked`, and `missing`, with last-edited visibility for both sides.
- Keep command handlers thin and delegate comparison, import planning, install planning, and sync decisions to catalog/core services.

**Non-Goals:**
- Building a remote or multi-user shared catalog service.
- Supporting arbitrary skill ecosystems beyond the known MDT/Claude/Copilot-oriented project locations in this change.
- Replacing the existing catalog item format wholesale; this change extends it for managed skills.
- Implementing a background file watcher or automatic sync daemon.

## Decisions

1. Introduce a dedicated managed-skill service layer on top of the catalog modules.
   - Decision: add headless services/value objects responsible for project discovery, import planning, status comparison, and sync planning rather than embedding that logic directly in command classes.
   - Rationale: the requested workflow spans multiple commands and requires deterministic comparison logic that should be testable without shell interaction.
   - Alternatives considered: extend each command independently with local filesystem scanning; rejected because comparison and default-selection behavior would drift across commands.

2. Treat the central MDT catalog as the canonical source and the project manifest as the per-project state ledger.
   - Decision: central skill content remains under the MDT config catalog, while `.mdt/catalog.json` stores how a given project installed or imported each managed skill, including hashes, install mode, logical consumers, physical path, and observed timestamps.
   - Rationale: this keeps one canonical editable source while preserving an auditable per-project record for status and sync decisions.
   - Alternatives considered: store project installation state inside the central catalog only; rejected because freshness/status is project-specific.

3. Model physical install locations separately from logical consumers.
   - Decision: extend managed skill metadata so one install definition can describe a physical project path plus one or more logical consumers that use that install.
   - Rationale: `.claude/skills/<name>/SKILL.md` can be the practical physical location while still being treated as usable by both Claude and Copilot in this workflow.
   - Alternatives considered: duplicate target definitions for each logical consumer with the same path; rejected because status and discovery would lose the explicit shared-location relationship.

4. Use content fingerprints as the primary freshness signal and timestamps as explanatory metadata.
   - Decision: compare central and project versions using stable content hashes/fingerprints, with filesystem modified times surfaced to the user as last-edited context and tie-break/explanation data.
   - Rationale: copied skills can have misleading timestamps, and symlinked skills can appear current even when the project file is not an independent copy. Hash-first comparison produces more reliable status states.
   - Alternatives considered: timestamps only; rejected because it is fragile and fails to distinguish equal content from clock skew or copied files.

5. Make import/install workflows selection-driven with deterministic defaults.
   - Decision: discovery results include a default-selected flag computed from classification heuristics; OpenSpec- and SpecKit-related skills are displayed but start deselected for project-to-central promotion.
   - Rationale: the user asked for explicit and predictable defaults without silently hiding skills.
   - Alternatives considered: hide those skills entirely or prompt ad hoc per skill; rejected because both reduce auditability and consistency.

6. Add dedicated catalog commands for import and status while extending install/sync/edit behavior.
   - Decision: keep the existing shell-first catalog namespace and add a project-to-central import command plus a managed-skill status command, while expanding install/sync/edit flows to operate on managed skill metadata.
   - Rationale: this matches MDT's current command architecture and keeps user workflows discoverable under one catalog area.
   - Alternatives considered: overload `catalog add` for import behavior; rejected because scaffolding a new item and importing an existing project skill are materially different flows.

## Risks / Trade-offs

- [Discovery heuristics classify a skill incorrectly] → Mitigation: keep discovery rules explicit, surface the detected location/consumers in status output, and allow rename/selection override during import.
- [Shared physical install locations complicate sync logic] → Mitigation: store physical path and logical consumers distinctly in both the item metadata and project manifest.
- [Copied installs drift after manual project edits] → Mitigation: track both central and installed fingerprints plus last-edited timestamps so status can show `project newer` versus `central newer` before sync.
- [More metadata increases manifest complexity] → Mitigation: keep the manifest schema additive and version-tolerant, with defaults for older records where possible.
- [Symlink safety differs across environments] → Mitigation: preserve the current fallback-to-copy behavior and record the actual install mode used.

## Migration Plan

1. Extend managed skill metadata and manifest loading so older catalog items and project manifests still load with safe defaults.
2. Add discovery/status services first, then update install/sync commands to record the richer metadata.
3. Introduce import and status commands after the underlying services are available.
4. Keep existing catalog list/add/remove behavior working for non-skill items.

## Open Questions

- Whether the shell import flow should be fully interactive, flag-driven, or support both modes can be finalized during implementation as long as rename and `mdt-` prefix choices remain guided and explicit.
- If future targets need different shared-location semantics, the install-definition model should be extended rather than reintroducing duplicated target-path mappings.

