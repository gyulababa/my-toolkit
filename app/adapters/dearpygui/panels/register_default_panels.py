# app/adapters/dearpygui/panels/register_default_panels.py
from __future__ import annotations

from helpers.toolkits.ui.runtime.windows import WindowFactoryRegistry

from .log_panel import build_toolkit_log_panel
from .about_panel import build_toolkit_about_panel


DEFAULT_PANEL_FACTORIES = {
    "toolkit.log_panel": build_toolkit_log_panel,
    "toolkit.about_panel": build_toolkit_about_panel,
}


def register_default_panels(factories: WindowFactoryRegistry) -> None:
    """
    Register toolkit-provided DPG panels under stable keys:
      - toolkit.log_panel
      - toolkit.about_panel
    """
    for key, factory in DEFAULT_PANEL_FACTORIES.items():
        factories.register(key, factory)
