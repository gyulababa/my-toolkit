from __future__ import annotations

import os

# Export the canonical ColorRGB used by helpers.
from helpers.color.color_types import ColorRGB  # noqa: F401


def pytest_configure(config) -> None:
    os.environ.setdefault("TZ", "UTC")
