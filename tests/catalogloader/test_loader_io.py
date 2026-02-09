# tests/catalogloader/test_loader_io.py
# Placeholder tests for catalogloader IO integration (expected to evolve as schema/loader contracts finalize).

from __future__ import annotations

from pathlib import Path

import pytest

# This is intentionally lightweight because CatalogLoader internals were not provided here.
# The goal is to assert that "load_raw/save_raw" behave consistently on JSON IO when available.


@pytest.mark.skip(reason="CatalogLoader contract not available in this test context yet.")
def test_loader_roundtrip(tmp_path: Path) -> None:
    """CatalogLoader should round-trip raw JSON to disk and back."""
    raise NotImplementedError
