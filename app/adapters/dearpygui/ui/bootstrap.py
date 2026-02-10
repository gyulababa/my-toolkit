# app/adapters/dearpygui/ui/bootstrap.py
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from helpers.runtime.optional_imports import require

from helpers.toolkits.ui.spec import load_ui_spec
from helpers.toolkits.ui.runtime import CommandRegistry, UiSession, WindowFactoryRegistry

from services.ui import UiStateService
from .dpg_host import DpgHost


def run_dpg_app(
    *,
    app_title: str,
    ui_spec_path: str | Path,
    persist_root: str | Path,
    helpers_root: Optional[str | Path] = None,
    register_commands: Callable[[CommandRegistry], None],
    register_windows: Callable[[WindowFactoryRegistry], None],
) -> int:
    dpg = require("dearpygui.dearpygui", pip_hint="dearpygui", purpose="Dockable UI host")

    spec = load_ui_spec(ui_spec_path)

    svc = UiStateService(
        persist_root=Path(persist_root),
        spec=spec,
        helpers_root=(Path(helpers_root) if helpers_root else None),
    )

    # Load last state (active doc)
    state = svc.load_active_state()

    cmds = CommandRegistry()
    factories = WindowFactoryRegistry()
    register_commands(cmds)
    register_windows(factories)

    dpg.create_context()
    dpg.create_viewport(title=app_title, width=1280, height=720)
    dpg.setup_dearpygui()

    host = DpgHost(dpg, factories=factories)
    session = UiSession(spec=spec, state=state, commands=cmds, factories=factories)
    _ctx = session.build(host=host, services=None)
    session.apply_state()

    dpg.show_viewport()

    while dpg.is_dearpygui_running() and not host.should_quit:
        dpg.render_dearpygui_frame()

    # Capture and persist last UI state as a new revision + set active.
    session.capture_state()
    svc.save_new_revision_from_state(session.state, note="ui autosave", make_active=True)

    dpg.destroy_context()
    return 0
