<!-- app/adapters/dearpygui/ui/README.md -->
app/adapters/dearpygui/ui
Purpose

DearPyGui adapter layer for the UI toolkit. It wires the runtime session to DearPyGui widgets and persists UI state via services.ui.

Module roles

bootstrap.py: Entry-point helper `run_dpg_app` that loads the UI spec, loads persisted UI state, registers commands/windows, builds the session, runs the DPG loop, and saves state on exit.

dpg_host.py: Implements helpers.toolkits.ui.runtime.UiHost and delegates window creation to DpgWindowManager.

dpg_menu_builder.py: Renders MenuSpec structures into DPG menu bars and forwards command/window toggle callbacks.

dpg_window_manager.py: Creates DPG windows from WindowSpec and bridges window state to/from helpers.toolkits.ui.state.WindowState.

Responsibilities

Create a DpgHost that implements helpers.toolkits.ui.runtime.UiHost.

Build and manage DearPyGui windows via DpgWindowManager.

Bootstrap a full session (load spec, load state, run loop, autosave).

Menu/window flow

run_dpg_app loads helpers.toolkits.ui.spec from disk, uses services.ui.UiStateService to restore state, then builds UiSession and DpgHost.

UiSession calls DpgHost.build_menus to render MenuSpec entries via dpg_menu_builder.

UiSession calls DpgHost.create_window for each WindowSpec; DpgWindowManager binds window handles for state apply/capture.

Boundaries

May import services.ui and helpers.toolkits.ui.

Must not import helpers.catalogloader or other persistence internals directly.

Public API (flat list)

run_dpg_app

DpgHost

DpgWindowManager
