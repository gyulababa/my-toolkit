# services/vision/persist_impl.py
# Choose ONE persisted loader implementation for the app.
# Canonical recommendation: helpers.persist.persisted_catalog_loader.PersistedCatalogLoader

from __future__ import annotations

from helpers.persist.persisted_catalog_loader import PersistedCatalogLoader  # :contentReference[oaicite:3]{index=3}

__all__ = ["PersistedCatalogLoader"]
