"""catalog_help command: show catalog usage guide with examples."""

from __future__ import annotations

from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult

HELP_TEXT = """\
Catalog — manage reusable instructions, prompts, skills, and agents.

Usage:

  1. Add a new item to the catalog:
     catalog add <name> --kind <skill|instruction|prompt|agent>

     Example: catalog add my-skill --kind skill
     Creates: ~/.config/mdt/catalog/my-skill/
               ├── catalog-item.yaml
               └── source/

  2. Edit the catalog item metadata or content:
     catalog edit <name>

     Opens catalog-item.yaml in $EDITOR. Fill in targets, tags, and source files.

     Example catalog-item.yaml:
       name: my-skill
       kind: skill
       description: "What this skill does"
       tags:
         language: [python]
         topic: [testing]
       targets:
         claude:
           install_mode: symlink
           path_template: ".claude/skills/{name}/SKILL.md"
         copilot:
           install_mode: symlink
           path_template: ".github/skills/{name}/SKILL.md"
         opencode:
           install_mode: render
           path_template: ".opencode/agents/{name}.md"
       source:
         files:
           - SKILL.md

     Then create your content at:
       ~/.config/mdt/catalog/my-skill/source/SKILL.md

  3. Import project skills into the central catalog:
     catalog import
     catalog import --all
     catalog import my-skill --as mdt-my-skill --prefix

     Discovers project skills from `.github/skills` and `.claude/skills`.
     Workflow-related skills are shown but deselected by default.

  4. List catalog items:
     catalog list
     catalog list --kind skill
     catalog list --target claude
     catalog list --language python

  5. Install a catalog item into the current project:
     catalog install <name> --target <claude|copilot|opencode>

     Example: catalog install my-skill --target claude
     Installs to: .claude/skills/my-skill/SKILL.md
     Tracked in:  .mdt/catalog.json

  6. Show managed skill status for the current project:
     catalog status

     Reports freshness state, install mode, path, logical consumers,
     and last-edited times for managed skills in the current project.

  7. Sync installed items after editing the canonical source:
     catalog sync

  8. Remove an installed item from the project:
     catalog remove <name>

Install modes:
  symlink — links to canonical source (auto-synced, same filesystem only)
  copy    — independent copy (tracked for later status/sync)
  render  — transforms content for target-specific format\
"""


class CatalogHelpCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        pass

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args, context
        return CommandResult(success=True, output=HELP_TEXT)

