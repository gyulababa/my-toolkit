<!-- services/ui/README.md -->
services/ui
Purpose

Domain services that bind UI state to persistence and history without depending on toolkit adapters.

Responsibilities

Provide UiStateService for loading the active UI state and saving revisions.

Own the persisted ui_state domain wiring via helpers.persist.

Expose service APIs consumed by UI adapters (e.g., DearPyGui).

Boundaries

May import helpers.toolkits.ui.* and helpers.persist.*

Must not import toolkit adapters or frontend frameworks.

Public API (flat list)

UiStateService
