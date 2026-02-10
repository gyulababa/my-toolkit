# helpers/toolkits/ui/runtime/ctx.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from helpers.toolkits.ui.spec import UiSpec
from helpers.toolkits.ui.state import UiState
from .events import UiEventBus
from .windows import UiHost


@dataclass
class UiCtx:
    spec: UiSpec
    state: UiState
    events: UiEventBus
    host: UiHost
    services: Any = None  # app-defined bag (optional)
