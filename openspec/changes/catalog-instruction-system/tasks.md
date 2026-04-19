## 1. Catalog Item Model

- [ ] 1.1 Create `src/mdt/catalog/__init__.py` package
- [ ] 1.2 Implement `CatalogItem` and `TargetConfig` dataclasses in `src/mdt/catalog/item.py` with YAML loading
- [ ] 1.3 Write tests for `CatalogItem` creation, YAML loading, and `TargetConfig.resolve_path()`

## 2. Catalog Registry

- [ ] 2.1 Implement `CatalogRegistry` in `src/mdt/catalog/registry.py` with `list_items()`, `get_item()`, and filtering by kind/tag/target
- [ ] 2.2 Implement configurable catalog root path with `MDT_CATALOG_PATH` env var fallback
- [ ] 2.3 Write tests for registry discovery, filtering, and path configuration

## 3. Catalog Renderer

- [ ] 3.1 Implement `CatalogRenderer` in `src/mdt/catalog/renderer.py` with target render function registration and passthrough default
- [ ] 3.2 Write tests for passthrough rendering, custom renderer registration, and metadata passing

## 4. Catalog Manifest

- [ ] 4.1 Implement `CatalogManifest` in `src/mdt/catalog/manifest.py` with load/save, record/remove, drift detection, and list
- [ ] 4.2 Write tests for manifest load/save, record/remove, drift detection, and empty manifest handling

## 5. Catalog Installer

- [ ] 5.1 Implement `CatalogInstaller` in `src/mdt/catalog/installer.py` with symlink/copy/render install modes
- [ ] 5.2 Implement symlink feasibility check and fallback to copy
- [ ] 5.3 Implement multi-file install support and manifest update on install
- [ ] 5.4 Write tests for all install modes, fallback behavior, unsupported target error, and manifest integration

## 6. Catalog Editor

- [ ] 6.1 Implement `CatalogEditor` in `src/mdt/catalog/editor.py` with `$EDITOR` resolution and fallback chain
- [ ] 6.2 Write tests for editor resolution, path construction, and error on missing editor

## 7. Catalog Commands

- [ ] 7.1 Implement `CatalogListCommand` in `src/mdt/commands/catalog_list.py`
- [ ] 7.2 Implement `CatalogAddCommand` in `src/mdt/commands/catalog_add.py`
- [ ] 7.3 Implement `CatalogInstallCommand` in `src/mdt/commands/catalog_install.py`
- [ ] 7.4 Implement `CatalogRemoveCommand` in `src/mdt/commands/catalog_remove.py`
- [ ] 7.5 Implement `CatalogSyncCommand` in `src/mdt/commands/catalog_sync.py`
- [ ] 7.6 Implement `CatalogEditCommand` in `src/mdt/commands/catalog_edit.py`
- [ ] 7.7 Write tests for each catalog command

## 8. Command Registry Integration

- [ ] 8.1 Register `catalog` category and all six catalog commands in `build_command_registry()`
- [ ] 8.2 Write test verifying catalog commands are registered under the "catalog" category

