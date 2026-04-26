"""catalog_status command: show managed skill freshness for the current project."""

from __future__ import annotations

from mdt.catalog.registry import CatalogRegistry
from mdt.core.context import ProjectContext
from mdt.core.registry import CommandRegistry
from mdt.core.result import CommandResult


class CatalogStatusCommand:
    def __init__(self, registry: CommandRegistry) -> None:
        del registry

    def __call__(self, args: list[str], context: ProjectContext) -> CommandResult:
        del args
        project_root = context.repo_root or context.cwd
        catalog = CatalogRegistry()
        statuses = catalog.get_managed_skill_statuses(project_root)
        if not statuses:
            return CommandResult(success=True, output="No managed skills found for this project.")

        lines = ["Managed skills:", ""]
        for status in statuses:
            consumers = ", ".join(status.logical_consumers) or "-"
            install_mode = status.install_mode or "-"
            path = status.installed_path or "-"
            lines.append(f"  {status.name}: {status.state}")
            lines.append(f"    mode: {install_mode}")
            lines.append(f"    path: {path}")
            lines.append(f"    consumers: {consumers}")
            lines.append(f"    central edited: {status.central_last_edited_at or '-'}")
            lines.append(f"    project edited: {status.project_last_edited_at or '-'}")
            lines.append("")
        return CommandResult(success=True, output="\n".join(lines).rstrip())

