# app/adapters/csvcleaner/recipes.py
from __future__ import annotations

from pathlib import Path
from typing import Any

from helpers.catalog import Catalog

from scripts.CSVcleaner.recipes_catalog_loader import RECIPES_LOADER
from scripts.CSVcleaner.recipes_schema import (
    CleaningRecipesResolved,
    RecipeResolved,
)


def load_recipes_resolved(path: str | Path, *, env_prefix: str = "OPS_") -> CleaningRecipesResolved:
    p = Path(path)
    raw = RECIPES_LOADER.load_raw(p)
    cat: Catalog[Any] = Catalog.load(
        raw,
        validate=RECIPES_LOADER.validate,
        schema_name=RECIPES_LOADER.schema_name,
        schema_version=RECIPES_LOADER.schema_version,
    )
    doc = cat.doc  # type: ignore[attr-defined]
    return doc.resolve(env_prefix=env_prefix)


__all__ = ["load_recipes_resolved", "CleaningRecipesResolved", "RecipeResolved"]
