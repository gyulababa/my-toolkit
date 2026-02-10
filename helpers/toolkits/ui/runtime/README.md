<!-- helpers/toolkits/ui/runtime/README.md -->
helpers/toolkits/ui/runtime
Purpose

Frontend-agnostic UI runtime helpers: sessions, commands, windows, and event wiring.

Key concepts

UiSession: ties spec, state, commands, and window factories together.

CommandRegistry: command execution and enabled predicates.

UiEventBus: in-memory event queue for simple runtime signaling.

UiHost: adapter interface for creating windows and menus.

WindowFactoryRegistry: maps factory keys to builders.

Runtime flow

Build UiSession with spec/state/registry/factories.

UiSession.build(host) creates windows, menus, and returns UiCtx.

UiSession.apply_state() and capture_state() are used by services to persist state (autosave orchestration lives outside this package).

Menu helpers

menu_enrich.enrich_menus_with_view_toggles adds View toggles without changing the source spec.

Belongs here

Runtime session and command helpers

Frontend-agnostic interfaces (UiHost, WindowHandle)

Does not belong here

Adapter rendering logic or persistence orchestration

Public API (flat list)

UiSession

CommandRegistry

UiEventBus

UiHost

WindowFactoryRegistry

WindowHandle

ExtraStateHooks
