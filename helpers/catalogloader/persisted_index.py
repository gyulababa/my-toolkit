# helpers/catalogloader/persisted_index.py
# Deprecated facade. Use helpers.persist.index/types instead.

from __future__ import annotations

from helpers.persist.index import read_index as load_index
from helpers.persist.index import write_index as save_index
from helpers.persist.types import PersistIndex

__all__ = ["PersistIndex", "load_index", "save_index"]
