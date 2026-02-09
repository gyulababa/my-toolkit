<!-- helpers/catalogloader/README.md -->
helpers/catalogloader
Purpose

Convention-based loader for JSON templates/configs stored under the helpers/ tree, per app:

templates: helpers/templates/<app_name>/*.json

configs: helpers/configs/<app_name>/*.json

Provides:

safe path construction (prevents traversal)

raw JSON load/save (delegating to helpers/fs, including atomic writes)

optional validation into Catalog

optional editable view (EditableCatalog)

Belongs here

Location conventions (templates/configs dirs)

Safe filename validation for template/config names

Load/save raw JSON using helpers/fs

High-level methods returning Catalog / EditableCatalog

Does not belong here

Schema definitions or domain validation logic → your app code (passed in as validate / dump)

Persistence of versions/active/latest semantics → helpers/persist

Undo/redo logic → helpers/history (injected into EditableCatalog)

Public API (flat list)

CatalogLoader

Properties:

root

templates_dir

configs_dir

Path helpers:

template_path(name) -> Path

config_path(name="default.json") -> Path

Listing:

list_templates(pattern="*.json") -> list[Path]

list_configs(pattern="*.json") -> list[Path]

Raw IO:

load_raw(path) -> dict

save_raw(path, raw, indent=2, sort_keys=True, overwrite=True) -> None

High-level loaders:

load_template_editable(name, history=None) -> EditableCatalog

load_config_editable(name="default.json", history=None) -> EditableCatalog

load_template_catalog(name) -> Catalog

load_config_catalog(name="default.json") -> Catalog

Saving:

save_editable(path, editable, validate_before_save=True) -> None

save_catalog(path, catalog) -> None