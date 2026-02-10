<!-- helpers/toolkits/ui/spec/README.md -->
helpers/toolkits/ui/spec
Purpose

UI spec models and helpers for file-driven UI configuration. Specs define commands, menus, and windows without binding to any specific frontend adapter.

Key concepts

UiSpec: versioned root document containing commands, menus, and windows.

CommandSpec: a command id/title with optional kind and enable predicate key.

MenuSpec: top-level menus composed of MenuItem entries (command, submenu, separator, window_toggle).

WindowSpec: window id/title/factory with optional dock hints and menu path.

DockHint: optional adapter hint for initial docking.

Serde + validation

load_ui_spec(path): parse JSON to UiSpec and validate ids and references.

dump_ui_spec(spec): convert UiSpec back to dict form for JSON emission.

validate_ui_spec(spec): enforce version and reference integrity.

File-driven menu design

Menu trees live in the spec file. Adapters can enrich menus (for example adding View toggles) without mutating the source JSON.

Belongs here

Spec models, serde, and validation logic

Does not belong here

Runtime session state, persistence, or adapter wiring

Public API (flat list)

UiSpec

CommandSpec

MenuSpec

MenuItem

WindowSpec

DockHint

load_ui_spec

dump_ui_spec

validate_ui_spec
