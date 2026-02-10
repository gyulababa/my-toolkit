# app/adapters/dearpygui/ui/bootstrap.py
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from helpers.runtime.optional_imports import require

from helpers.toolkits.ui.spec.serde import load_ui_spec
from helpers.toolkits.ui.runtime.commands import CommandRegistry
from helpers.toolkits.ui.runtime.windows import WindowFactoryRegistry
from helpers.toolkits.ui.runtime.session import UiSession
from helpers.toolkits.ui.runtime.autosave import UiStateAutosaver

from services.ui.ui_state_service import UiStateService
from .dpg_host import DpgHost


def run_dpg_app(
    *,
    app_title: str,
    ui_spec_path: str | Path,
    persist_root: str | Path,
    helpers_root: Optional[str | Path] = None,
    autosave_interval_s: float = 2.0,
    register_commands: Callable[[CommandRegistry], None],
    register_windows: Callable[[WindowFactoryRegistry], None],
) -> int:
    dpg = require("dearpygui.dearpygui", pip_hint="dearpygui", purpose="Dockable UI host")

    spec = load_ui_spec(ui_spec_path)
    window_title_by_id = {w.id: w.title for w in spec.windows}

    helpers_root_path = Path(helpers_root).resolve() if helpers_root else None
    svc = UiStateService(
        persist_root=Path(persist_root),
        spec=spec,
        helpers_root=helpers_root_path,
    )

    state = svc.load_active_state()

    # NEW: allow runtime spec arg refs (configs:...) to resolve
    if helpers_root_path:
        state.kv["_helpers_root"] = str(helpers_root_path)

    cmds = CommandRegistry()
    factories = WindowFactoryRegistry()
    register_commands(cmds)
    register_windows(factories)

    dpg.create_context()
    dpg.create_viewport(title=app_title, width=1280, height=720)
    dpg.setup_dearpygui()

    host = DpgHost(dpg, factories=factories, window_title_by_id=window_title_by_id)
    session = UiSession(spec=spec, state=state, commands=cmds, factories=factories)
    ctx = session.build(host=host, services=None)
    session.apply_state()

    autosaver = UiStateAutosaver(interval_s=autosave_interval_s)

    def save_now(note: str = "ui autosave") -> None:
        session.capture_state()
        svc.save_new_revision_from_state(session.state, note=note, make_active=True)

    dpg.show_viewport()

    while dpg.is_dearpygui_running() and not host.should_quit:
        dpg.render_dearpygui_frame()

        for ev in ctx.events.drain():
            if ev.type == "state_dirty":
                autosaver.mark_dirty()

        autosaver.pump(lambda: save_now("ui autosave"))

    save_now("ui exit save")

    dpg.destroy_context()
    return 0
