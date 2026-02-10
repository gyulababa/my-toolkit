# helpers/toolkits/ui/runtime/events.py
from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any, Dict, List


@dataclass(frozen=True)
class UiEvent:
    type: str
    payload: Dict[str, Any]
    ts: float


class UiEventBus:
    def __init__(self) -> None:
        self._events: List[UiEvent] = []

    def emit(self, type: str, **payload: Any) -> None:
        self._events.append(UiEvent(type=type, payload=dict(payload), ts=time()))

    def drain(self) -> List[UiEvent]:
        out = self._events[:]
        self._events.clear()
        return out
