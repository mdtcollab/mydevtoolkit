from mdt.commands.catalog_add import CatalogAddCommand
from mdt.commands.catalog_edit import CatalogEditCommand
from mdt.commands.catalog_help import CatalogHelpCommand
from mdt.commands.catalog_import import CatalogImportCommand
from mdt.commands.catalog_install import CatalogInstallCommand
from mdt.commands.catalog_list import CatalogListCommand
from mdt.commands.catalog_remove import CatalogRemoveCommand
from mdt.commands.catalog_status import CatalogStatusCommand
from mdt.commands.catalog_sync import CatalogSyncCommand
from mdt.commands.exit import ExitCommand
from mdt.commands.git_branch import GitBranchCommand
from mdt.commands.help import HelpCommand
from mdt.commands.openspec_branch import OpenspecBranchCommand
from mdt.commands.openspec_finish import OpenspecFinishCommand
from mdt.commands.settings_editor_set import SettingsEditorSetCommand
from mdt.commands.settings_theme_set import SettingsThemeSetCommand
from mdt.commands.workflow_record import WorkflowRecordCommand
from mdt.commands.workflow_status import WorkflowStatusCommand
from mdt.core.registry import CommandRegistry


def build_command_registry() -> CommandRegistry:
    registry = CommandRegistry()
    registry.register_category("openspec")
    registry.register_category("git")
    registry.register_category("copilot")
    registry.register_category("settings")
    registry.register_category("catalog")
    registry.register_category("workflow")
    registry.register("help", HelpCommand)
    registry.register("exit", ExitCommand)
    registry.register("openspec_branch", OpenspecBranchCommand, category="openspec")
    registry.register("openspec_finish", OpenspecFinishCommand, category="openspec")
    registry.register("git_branch", GitBranchCommand, category="git")
    registry.register("settings_editor_set", SettingsEditorSetCommand, category="settings")
    registry.register("settings_theme_set", SettingsThemeSetCommand, category="settings")
    registry.register("catalog_list", CatalogListCommand, category="catalog")
    registry.register("catalog_add", CatalogAddCommand, category="catalog")
    registry.register("catalog_import", CatalogImportCommand, category="catalog")
    registry.register("catalog_install", CatalogInstallCommand, category="catalog")
    registry.register("catalog_remove", CatalogRemoveCommand, category="catalog")
    registry.register("catalog_status", CatalogStatusCommand, category="catalog")
    registry.register("catalog_sync", CatalogSyncCommand, category="catalog")
    registry.register("catalog_edit", CatalogEditCommand, category="catalog")
    registry.register("catalog_help", CatalogHelpCommand, category="catalog")
    registry.register("workflow_record", WorkflowRecordCommand, category="workflow")
    registry.register("workflow_status", WorkflowStatusCommand, category="workflow")
    return registry


COMMAND_REGISTRY = build_command_registry()
