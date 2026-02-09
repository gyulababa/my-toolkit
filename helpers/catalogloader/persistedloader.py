# helpers/catalogloader/persistedloader.py
# Deprecated facade. Use helpers.persist.persisted_catalog_loader instead.

from __future__ import annotations

import warnings

from helpers.persist.persisted_catalog_loader import PersistedCatalogLoader

warnings.warn(
    "helpers.catalogloader.persistedloader is deprecated; use helpers.persist.persisted_catalog_loader",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["PersistedCatalogLoader"]
