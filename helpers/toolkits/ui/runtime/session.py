# helpers/toolkits/ui/runtime/session.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from helpers.toolkits.ui.spec.models import UiSpec
from helpers.toolkits.ui.state.models import UiState
from .commands import CommandRegistry
from .ctx import UiCtx
from .events import UiEventBus
from .windows import UiHost, WindowFactoryRegistry, WindowHandle
from .menu_enrich import enrich_menus


@dataclass
class UiSession:
    spec: UiSpec
    state: UiState
    commands: CommandRegistry
    factories: WindowFactoryRegistry

    _handles: Optional[Dict[str, WindowHandle]] = None

    def build(self, host: UiHost, services: object | None = None) -> UiCtx:
        self._handles = {}
        events = UiEventBus()
        ctx = UiCtx(spec=self.spec, state=self.state, events=events, host=host, services=services)

        def on_command(command_id: str, payload: Optional[dict] = None) -> None:
            self.commands.execute(command_id, ctx, payload)

        def on_window_toggle(window_id: str) -> None:
            self.toggle_window(window_id)
            ctx.events.emit("state_dirty", reason="window_toggle", window_id=window_id)

        effective_menus = enrich_menus(self.spec)
        host.build_menus(effective_menus, on_command=on_command, on_window_toggle=on_window_toggle)

        for w in self.spec.windows:
            if not self.factories.has(w.factory):
                raise KeyError(f"Window {w.id} references unregistered factory: {w.factory}")
            handle = host.create_window(w, w.factory, ctx)
            self._handles[w.id] = handle

        return ctx

    def apply_state(self) -> None:
        assert self._handles is not None
        for win_id, handle in self._handles.items():
            ws = self.state.get_window(win_id)
            handle.apply_state(ws)

    def capture_state(self) -> None:
        assert self._handles is not None
        for win_id, handle in self._handles.items():
            self.state.windows[win_id] = handle.capture_state()

    def toggle_window(self, window_id: str) -> None:
        assert self._handles is not None
        if window_id not in self._handles:
            raise KeyError(f"Unknown window_id: {window_id}")
        h = self._handles[window_id]
        new_open = not h.is_open()
        h.set_open(new_open)
        ws = self.state.get_window(window_id)
        ws.is_open = new_open
