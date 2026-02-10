<!-- helpers/toolkits/ui/state/README.md -->
helpers/toolkits/ui/state
Purpose

UI state models and helpers for persisted UI state: defaults, migration, serde, and CatalogLoader integration.

Key concepts

UiState: versioned root containing window state, layout hints, and app-level kv.

WindowState: per-window open/pos/size plus optional extra data blob.

Defaults

default_ui_state_from_spec(spec): derive initial UiState from UiSpec windows.

Migration

migrate_state_dict(raw): normalize and upgrade raw dicts to the latest schema.

Serde

ensure_ui_state(raw): validate and coerce dict data to UiState.

dump_ui_state(state): convert UiState to raw dict for persistence.

load_ui_state(path): read JSON and return UiState (defaults when missing).

Loader integration

make_ui_state_catalog_loader(): build a CatalogLoader configured for ui_state persistence.

Belongs here

State models, defaults, migrations, and serde helpers

Does not belong here

Adapter wiring, history orchestration, or UI runtime logic

Public API (flat list)

UiState

WindowState

default_ui_state_from_spec

ensure_ui_state

dump_ui_state

load_ui_state

save_ui_state

make_ui_state_catalog_loader
