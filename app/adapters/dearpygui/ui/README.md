<!-- app/adapters/dearpygui/ui/README.md -->
app/adapters/dearpygui/ui
Purpose

DearPyGui adapter layer for the UI toolkit: host implementation, window manager, and bootstrap wiring.

Responsibilities

Create a DpgHost that implements helpers.toolkits.ui.runtime.UiHost.

Build and manage DearPyGui windows via DpgWindowManager.

Bootstrap a full session (load spec, load state, run loop, autosave).

Boundaries

May import services.ui and helpers.toolkits.ui.

Must not import helpers.catalogloader or other persistence internals directly.

Public API (flat list)

run_dpg_app

DpgHost

DpgWindowManager
