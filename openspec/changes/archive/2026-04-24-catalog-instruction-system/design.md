## Context

MDT is a Python CLI tool with an interactive shell (`mdt`) built on a thin-UI / headless-core architecture. Commands are registered in a `CommandRegistry`, dispatched by `CommandDispatcher`, and operate on a `ProjectContext` that knows the repo root and project name. Currently MDT has no mechanism for managing reusable development content (instructions, prompts, skills, agent definitions) or installing them into projects for different AI coding tools.

The target AI tools each expect content in different locations and formats:
- **Claude**: `.claude/` directory with `CLAUDE.md`, skills in `.claude/skills/`, etc.
- **GitHub Copilot**: `.github/copilot-instructions.md`, prompts in `.github/prompts/`, skills in `.github/skills/`
- **OpenCode**: `.opencode/` directory with `agents.md`, instructions, etc.

## Goals / Non-Goals

**Goals:**
- Define a catalog item data model supporting kind (instruction, prompt, skill, agent), classification tags (language, topic, domain), and target compatibility.
- Store canonical catalog items in a well-known location managed by MDT.
- Install catalog items into a target project using the appropriate strategy (symlink, copy, or render).
- Track installed items per-project in a manifest so MDT can update, remove, and sync.
- Provide MDT shell commands under a `catalog` category for list, add, install, edit, remove, sync operations.
- Open catalog items in `$EDITOR` for maintenance from within MDT.
- Keep all business logic in `src/mdt/catalog/` (core layer), with commands as thin wrappers.

**Non-Goals:**
- Remote catalog servers or package-registry-style distribution (local-only for now).
- Auto-detection of which catalog items a project needs.
- GUI or web interface for catalog management.
- Supporting arbitrary custom target formats beyond Claude, Copilot, and OpenCode.

## Decisions

### 1. Catalog storage location

**Decision**: Store the canonical catalog under `~/.config/mdt/catalog/` (XDG-compliant), with each item in its own directory containing a `catalog-item.yaml` metadata file and source files.

**Rationale**: Keeping the catalog outside any single project makes it reusable across projects. XDG compliance is standard for CLI tools on Linux. The alternative of embedding the catalog inside the MDT source tree was rejected because it couples catalog content to MDT releases.

**Structure**:
```
~/.config/mdt/catalog/
  <item-name>/
    catalog-item.yaml    # metadata: kind, tags, targets, source files
    source/              # canonical content files
      SKILL.md
      ...
```

### 2. Catalog item metadata model

**Decision**: Each catalog item has a `catalog-item.yaml` with:
```yaml
kind: skill | instruction | prompt | agent
name: openspec-propose
description: "Propose a new change..."
tags:
  language: [python]       # optional, can be empty for language-agnostic
  topic: [openspec, workflow]
  domain: [development]
targets:
  claude:
    install_mode: copy | symlink | render
    path_template: ".claude/skills/{name}/SKILL.md"
  copilot:
    install_mode: copy | symlink | render
    path_template: ".github/skills/{name}/SKILL.md"
  opencode:
    install_mode: render
    path_template: ".opencode/agents/{name}.md"
source:
  files:
    - SKILL.md
```

**Rationale**: YAML is consistent with the rest of the project (openspec uses YAML). The multi-dimensional tagging (language, topic, domain) avoids a language-only taxonomy. Per-target configuration in the same file keeps everything in one place.

### 3. Install strategies

**Decision**: Three install modes per target:
- **symlink**: Create a symlink from the project to the canonical catalog source. Used when the target format exactly matches the canonical source.
- **copy**: Copy the file. Used when symlinks are unreliable (e.g., cross-filesystem, Windows, or when the user prefers independence).
- **render**: Transform the canonical source into a target-specific format using a renderer. Used when Claude/Copilot/OpenCode expect structurally different files from the same content.

**Rationale**: Symlinks avoid duplication and keep content in sync automatically. Copy is a safe fallback. Render handles the case where targets need genuinely different file structures (e.g., OpenCode's agent format differs from Claude's skill format).

**Symlink safety rule**: Symlink is safe when (a) the canonical source and project are on the same filesystem, and (b) the target format is identical to the source format. The installer SHALL verify these conditions and fall back to copy if symlink would fail.

### 4. Project manifest for tracking

**Decision**: Installed items are tracked in `.mdt/catalog.json` at the project root:
```json
{
  "items": {
    "openspec-propose": {
      "kind": "skill",
      "install_mode": "symlink",
      "target": "claude",
      "installed_path": ".claude/skills/openspec-propose/SKILL.md",
      "source_hash": "abc123...",
      "installed_at": "2026-04-19T10:00:00Z"
    }
  }
}
```

**Rationale**: JSON is easy to read/write from Python. Storing the source hash enables drift detection during sync. The `.mdt/` directory is a natural place for MDT project metadata without conflicting with other tool directories.

### 5. Renderer architecture

**Decision**: A `CatalogRenderer` class with target-specific render methods. Each target registers a rendering function that takes canonical source content and produces target-formatted output. Initially simple (mostly passthrough or light Jinja2 templating); can be extended later.

**Alternative considered**: A plugin system with dynamic renderer loading. Rejected as over-engineering for three known targets.

### 6. Editor integration

**Decision**: `catalog edit <item-name>` opens the canonical source file in `$EDITOR` (falling back to `nano`, then `vi`). The command uses `subprocess.run()` with the editor process attached to the terminal.

**Rationale**: This is the standard Unix pattern. Editing the canonical source rather than installed copies ensures changes propagate on next sync.

### 7. Command structure

**Decision**: Commands under a `catalog` category:
- `catalog_list` — List catalog items, optionally filtered by kind/language/topic/target
- `catalog_add` — Add a new item to the catalog (scaffolds directory + metadata)
- `catalog_install` — Install a catalog item into the current project for a target
- `catalog_remove` — Remove an installed catalog item from the project
- `catalog_sync` — Re-sync all installed items (detect drift, update changed items)
- `catalog_edit` — Open a catalog item in an external editor

**Rationale**: Follows the existing command naming pattern (underscore-separated, registered with category). Each command is a thin wrapper calling into `src/mdt/catalog/` core modules.

## Risks / Trade-offs

- **[Symlink portability]** → Symlinks may not work on all platforms or across filesystems. Mitigation: the installer validates symlink feasibility and falls back to copy mode automatically.
- **[Catalog location discovery]** → Users may want a different catalog location. Mitigation: make the catalog path configurable via environment variable `MDT_CATALOG_PATH` or a config setting.
- **[Render complexity]** → Target formats may diverge significantly over time. Mitigation: start with simple renderers; the architecture allows adding more sophisticated ones without changing the item model.
- **[Manifest drift]** → Users may manually edit or delete installed files. Mitigation: `catalog_sync` detects missing or changed files and offers to re-install.

