"""catalog_import command: import discovered project skills into the central catalog."""

from __future__ import annotations

from mdt.catalog.managed_skills import import_project_skill
from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogImportCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        project_root = context.repo_root or context.cwd
        catalog = CatalogRegistry()
        discovered = catalog.discover_project_skills(project_root)
        if not discovered:
            return CommandResult(success=True, output="No project skills found in known locations.")

        selected_names: list[str] = []
        rename_map: dict[str, str] = {}
        add_prefix = False
        import_all = False
        include_deselected = False
        single_alias: str | None = None

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--all":
                import_all = True
                i += 1
            elif arg == "--include-deselected":
                include_deselected = True
                i += 1
            elif arg == "--prefix":
                add_prefix = True
                i += 1
            elif arg == "--as" and i + 1 < len(args):
                single_alias = args[i + 1]
                i += 2
            elif arg == "--rename" and i + 1 < len(args):
                mapping = args[i + 1]
                if "=" in mapping:
                    source, destination = mapping.split("=", 1)
                    rename_map[source] = destination
                i += 2
            elif arg.startswith("--"):
                i += 1
            else:
                selected_names.append(arg)
                i += 1

        if not selected_names and not import_all:
            lines = [
                "Discovered project skills:",
                "",
            ]
            for skill in discovered:
                selected_marker = "x" if skill.default_selected else " "
                reason = "default" if skill.default_selected else "deselected by default (workflow-related)"
                consumers = ", ".join(skill.logical_consumers)
                lines.append(
                    f"  [{selected_marker}] {skill.name} -> {skill.name} "
                    f"(path: {skill.primary_relative_path}; consumers: {consumers}; {reason})"
                )
            lines.extend([
                "",
                "Use `catalog import --all` to import default-selected skills, `--include-deselected` to include workflow skills,",
                "or `catalog import <name> [--as <new-name>] [--prefix]` to choose explicitly.",
            ])
            return CommandResult(success=True, output="\n".join(lines))

        by_name = {skill.name: skill for skill in discovered}
        if import_all:
            selected_skills = [
                skill for skill in discovered
                if skill.default_selected or include_deselected
            ]
        else:
            selected_skills = []
            for name in selected_names:
                skill = by_name.get(name)
                if skill is None:
                    return CommandResult(success=False, error=f"Project skill '{name}' not found.")
                selected_skills.append(skill)

        if single_alias and len(selected_skills) != 1:
            return CommandResult(success=False, error="--as can only be used when importing a single skill.")
        if not selected_skills:
            return CommandResult(success=False, error="No skills selected for import.")

        results = []
        for skill in selected_skills:
            result = import_project_skill(
                project_root,
                catalog.root,
                skill,
                rename_to=single_alias if len(selected_skills) == 1 else rename_map.get(skill.name),
                add_prefix=add_prefix,
            )
            results.append(f"  - {result.source_name} -> {result.imported_name}")

        return CommandResult(
            success=True,
            output="Imported skills into the central catalog:\n" + "\n".join(results),
        )

    @staticmethod
    def get_completions(position: int, tokens: list[str]) -> list[str]:
        if position == 0:
            from mdt.core.context import ProjectContext

            prefix = tokens[0].lower() if tokens else ""
            try:
                ctx = ProjectContext.detect()
                project_root = ctx.repo_root or ctx.cwd
                catalog = CatalogRegistry()
                return [
                    skill.name for skill in catalog.discover_project_skills(project_root)
                    if skill.name.startswith(prefix)
                ]
            except Exception:  # noqa: BLE001
                return []
        prefix = tokens[position].lower() if position < len(tokens) else ""
        flags = ["--all", "--as", "--include-deselected", "--prefix", "--rename"]
        return [flag for flag in flags if flag.startswith(prefix)]


