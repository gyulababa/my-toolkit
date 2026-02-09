# helpers/catalogloader/loader.py
# Deprecated facade. Use helpers.persist.loader instead.

from __future__ import annotations

import warnings

from helpers.persist.loader import CatalogLoader

warnings.warn(
    "helpers.catalogloader.loader is deprecated; use helpers.persist.loader",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["CatalogLoader"]
