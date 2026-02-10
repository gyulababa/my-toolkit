# scripts/CSVcleaner/recipes_schema.py
# cleaning/recipes_schema.py
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from helpers.validation import ValidationError

_VAR_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _expand_vars(s: str, vars_map: Mapping[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        return str(vars_map.get(key, m.group(0)))
    return _VAR_PATTERN.sub(repl, s)


def _normalize_list(v: Any) -> List[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    if isinstance(v, str):
        return [x.strip() for x in v.split(",") if x.strip()]
    return [str(v)]


@dataclass(frozen=True)
class RecipeSpec:
    id: str
    description: str = ""
    input_default: str = ""
    output_default: str = ""
    keep: List[str] = None  # type: ignore[assignment]
    rename: Dict[str, str] = None  # type: ignore[assignment]
    html_col: str = ""
    meta_cols: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        object.__setattr__(self, "keep", self.keep or [])
        object.__setattr__(self, "rename", self.rename or {})
        object.__setattr__(self, "meta_cols", self.meta_cols or [])


@dataclass(frozen=True)
class CleaningRecipesDoc:
    """
    Persistable, schema-validated config doc for CSV cleaning recipes.
    Store this via CatalogLoader (and optionally PersistedCatalogLoader).
    """
    vars: Dict[str, str]
    recipes: List[RecipeSpec]
    quickruns: Dict[str, List[str]]  # quickrun_id -> recipe_ids

    def resolve(self, *, env_prefix: str = "OPS_") -> "CleaningRecipesResolved":
        """
        Apply env overrides and ${VAR} expansion to defaults.
        """
        vars_map = dict(self.vars)

        # Allow env overrides: OPS_DATA_DIR overrides vars["DATA_DIR"], etc.
        for k in list(vars_map.keys()):
            env_k = f"{env_prefix}{k}"
            if env_k in os.environ:
                vars_map[k] = os.environ[env_k]

        def expand(x: str) -> str:
            return _expand_vars(str(x), vars_map)

        resolved_recipes: Dict[str, RecipeResolved] = {}
        for r in self.recipes:
            rid = str(r.id).strip()
            if not rid:
                raise ValidationError("recipes[].id must be non-empty")
            if rid in resolved_recipes:
                raise ValidationError(f"Duplicate recipe id: {rid}")

            resolved_recipes[rid] = RecipeResolved(
                id=rid,
                description=str(r.description or ""),
                input_default=expand(r.input_default or ""),
                output_default=expand(r.output_default or ""),
                keep=list(r.keep or []),
                rename=dict(r.rename or {}),
                html_col=str(r.html_col or "").strip(),
                meta_cols=_normalize_list(r.meta_cols),
            )

        # Validate quickruns refer to existing recipes
        for qid, ids in (self.quickruns or {}).items():
            if not str(qid).strip():
                raise ValidationError("quickruns keys must be non-empty strings")
            for rid in ids:
                if rid not in resolved_recipes:
                    raise ValidationError(f"quickrun '{qid}' references unknown recipe id: {rid}")

        return CleaningRecipesResolved(
            vars=vars_map,
            recipes=resolved_recipes,
            quickruns={k: list(v) for k, v in (self.quickruns or {}).items()},
        )


@dataclass(frozen=True)
class RecipeResolved:
    id: str
    description: str
    input_default: str
    output_default: str
    keep: List[str]
    rename: Dict[str, str]
    html_col: str
    meta_cols: List[str]


@dataclass(frozen=True)
class CleaningRecipesResolved:
    vars: Dict[str, str]
    recipes: Dict[str, RecipeResolved]          # recipe_id -> resolved spec
    quickruns: Dict[str, List[str]]             # quickrun_id -> recipe_ids
