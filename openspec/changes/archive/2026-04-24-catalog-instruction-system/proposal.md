## Why

MDT currently has no way to manage or distribute reusable development guidelines, prompts, skills, or agent definitions across projects. Each project must manually set up its `.github/`, `.claude/`, or other tool-specific directories. This leads to duplicated, drifting content and no single source of truth. A catalog-driven instruction system lets MDT maintain canonical content centrally and install it into any project for Claude, GitHub Copilot, OpenCode, or future targets.

## What Changes

- Introduce a **catalog** subsystem: a local registry of reusable content items (instructions, prompts, skills, agents) managed by MDT.
- Each catalog item has metadata (kind, language, topic, target compatibility) and canonical source files.
- Add an **installer** that copies, symlinks, or renders catalog items into a target project's tool-specific directories (`.claude/`, `.github/`, `.opencode/`, etc.).
- Add **project manifest tracking** so MDT knows which catalog items are installed in a project and can update, remove, or resync them.
- Add **MDT shell commands** for managing catalog content: `catalog list`, `catalog add`, `catalog install`, `catalog edit`, `catalog remove`, `catalog sync`.
- Support **symlink mode** when the target format matches the canonical source, and **render mode** when target-specific transformation is needed.

## Capabilities

### New Capabilities
- `catalog-registry`: Central catalog storage, item metadata model, discovery, and filtering by kind/language/topic/target.
- `catalog-item-model`: Data model for a catalog item including kind, classification tags, target compatibility, and source file references.
- `catalog-installer`: Install catalog items into a project for a given target (Claude/Copilot/OpenCode) using copy, symlink, or render strategies.
- `catalog-manifest`: Per-project manifest tracking which catalog items are installed, their install mode, and source version for update/remove/sync.
- `catalog-renderer`: Transform canonical catalog source files into target-specific formats when direct symlink is not possible.
- `catalog-editor`: Open a catalog item's canonical source in an external editor (`$EDITOR`, `nano`, etc.) from within MDT.
- `catalog-commands`: MDT shell commands for catalog operations (list, add, install, edit, remove, sync).

### Modified Capabilities
- `command-registry`: New catalog commands will be registered alongside existing commands.

## Impact

- New `src/mdt/catalog/` package with registry, item model, installer, manifest, renderer, and editor modules.
- New `src/mdt/commands/catalog_*.py` command files registered in the command registry.
- New `catalog/` directory at MDT's data location for storing canonical catalog items.
- Per-project `.mdt/catalog-manifest.json` (or similar) file for tracking installed items.
- No breaking changes to existing commands or shell behavior.

