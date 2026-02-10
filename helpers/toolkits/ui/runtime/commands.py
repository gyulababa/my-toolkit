# helpers/toolkits/ui/runtime/commands.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from .ctx import UiCtx


CommandFn = Callable[[UiCtx, Optional[dict]], None]
EnabledFn = Callable[[UiCtx], bool]


@dataclass
class _CmdEntry:
    fn: CommandFn
    enabled_when: Optional[EnabledFn] = None


class CommandRegistry:
    def __init__(self) -> None:
        self._cmds: Dict[str, _CmdEntry] = {}

    def register(self, command_id: str, fn: CommandFn, enabled_when: Optional[EnabledFn] = None) -> None:
        if command_id in self._cmds:
            raise ValueError(f"Command already registered: {command_id}")
        self._cmds[command_id] = _CmdEntry(fn=fn, enabled_when=enabled_when)

    def is_enabled(self, command_id: str, ctx: UiCtx) -> bool:
        ent = self._cmds.get(command_id)
        if ent is None:
            return False
        if ent.enabled_when is None:
            return True
        return bool(ent.enabled_when(ctx))

    def execute(self, command_id: str, ctx: UiCtx, payload: Optional[dict] = None) -> None:
        ent = self._cmds.get(command_id)
        if ent is None:
            raise KeyError(f"Unknown command_id: {command_id}")
        if ent.enabled_when is not None and not ent.enabled_when(ctx):
            return
        ent.fn(ctx, payload)
        ctx.events.emit("command_executed", command_id=command_id)
