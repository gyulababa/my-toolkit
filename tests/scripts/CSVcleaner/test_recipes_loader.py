# tests/scripts/CSVcleaner/test_recipes_loader.py
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from helpers.validation import ValidationError


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from CSVcleaner.recipes_catalog_loader import RECIPES_LOADER  # noqa: E402
from CSVcleaner.recipes_schema import CleaningRecipesDoc  # noqa: E402


def _base_raw() -> dict:
    return {
        "vars": {"DATA_DIR": "C:/data"},
        "recipes": [
            {
                "id": "r1",
                "description": "Test",
                "input_default": "${DATA_DIR}/in.csv",
                "output_default": "${DATA_DIR}/out.csv",
                "keep": ["a", "b"],
                "rename": {"A": "a"},
                "html_col": "html",
                "meta_cols": ["tags"],
            }
        ],
        "quickruns": {"qr1": ["r1"]},
    }


def test_validate_duplicate_recipe_ids() -> None:
    raw = _base_raw()
    raw["recipes"].append(dict(raw["recipes"][0]))

    with pytest.raises(ValidationError, match="Duplicate recipe id"):
        RECIPES_LOADER.validate(raw)


def test_validate_unknown_quickrun_refs() -> None:
    raw = _base_raw()
    raw["quickruns"] = {"qr1": ["missing"]}

    with pytest.raises(ValidationError, match="unknown recipe id"):
        RECIPES_LOADER.validate(raw)


def test_resolve_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = _base_raw()
    doc = RECIPES_LOADER.validate(raw)
    assert isinstance(doc, CleaningRecipesDoc)

    monkeypatch.setenv("OPS_DATA_DIR", "D:/override")
    resolved = doc.resolve(env_prefix="OPS_")

    r = resolved.recipes["r1"]
    assert r.input_default == "D:/override/in.csv"
    assert r.output_default == "D:/override/out.csv"


def test_resolve_var_expansion_without_env() -> None:
    raw = _base_raw()
    doc = RECIPES_LOADER.validate(raw)

    resolved = doc.resolve(env_prefix="OPS_")
    r = resolved.recipes["r1"]
    assert r.input_default == "C:/data/in.csv"
    assert r.output_default == "C:/data/out.csv"
