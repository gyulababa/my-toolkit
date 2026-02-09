# cleaning/recipes_catalog_loader.py
from __future__ import annotations

from typing import Any, Dict, List, Mapping

from helpers.persist.catalog_loader import CatalogLoader
from helpers.validation import ValidationError

from .recipes_schema import CleaningRecipesDoc, RecipeSpec


SCHEMA_NAME = "cleaning_recipes"
SCHEMA_VERSION = 1


def _as_str_map(x: Any) -> Dict[str, str]:
    if x is None:
        return {}
    if not isinstance(x, dict):
        raise ValidationError("vars must be an object")
    out: Dict[str, str] = {}
    for k, v in x.items():
        kk = str(k)
        out[kk] = str(v)
    return out


def _parse_recipe(raw: Mapping[str, Any]) -> RecipeSpec:
    if not isinstance(raw, dict):
        raise ValidationError("recipes[] items must be objects")

    rid = str(raw.get("id", "")).strip()
    if not rid:
        raise ValidationError("recipes[].id must be non-empty")

    rename = raw.get("rename") or {}
    if not isinstance(rename, dict):
        raise ValidationError(f"recipes[{rid}].rename must be an object")

    return RecipeSpec(
        id=rid,
        description=str(raw.get("description") or ""),
        input_default=str(raw.get("input_default") or ""),
        output_default=str(raw.get("output_default") or ""),
        keep=list(raw.get("keep") or []) if isinstance(raw.get("keep"), list) else [],
        rename={str(k): str(v) for k, v in rename.items()},
        html_col=str(raw.get("html_col") or "").strip(),
        meta_cols=list(raw.get("meta_cols") or []) if isinstance(raw.get("meta_cols"), list) else [],
    )


def validate_cleaning_recipes(raw: Dict[str, Any]) -> CleaningRecipesDoc:
    if not isinstance(raw, dict):
        raise ValidationError("Doc must be an object")

    vars_map = _as_str_map(raw.get("vars"))

    recipes_raw = raw.get("recipes") or []
    if not isinstance(recipes_raw, list):
        raise ValidationError("recipes must be a list")

    recipes: List[RecipeSpec] = []
    seen = set()
    for r in recipes_raw:
        spec = _parse_recipe(r)
        if spec.id in seen:
            raise ValidationError(f"Duplicate recipe id: {spec.id}")
        seen.add(spec.id)
        recipes.append(spec)

    quickruns_raw = raw.get("quickruns") or {}
    if isinstance(quickruns_raw, list):
        # Back-compat with old shape: [{"id": "...", "recipe_ids":[...]}]
        qr: Dict[str, List[str]] = {}
        for q in quickruns_raw:
            if not isinstance(q, dict):
                raise ValidationError("quickruns[] items must be objects")
            qid = str(q.get("id", "")).strip()
            if not qid:
                raise ValidationError("quickruns[].id must be non-empty")
            recipe_ids = q.get("recipe_ids") or []
            if not isinstance(recipe_ids, list):
                raise ValidationError(f"quickruns[{qid}].recipe_ids must be a list")
            qr[qid] = [str(x) for x in recipe_ids]
        quickruns = qr
    elif isinstance(quickruns_raw, dict):
        quickruns = {str(k): [str(x) for x in (v or [])] for k, v in quickruns_raw.items()}
    else:
        raise ValidationError("quickruns must be an object or a list")

    # Light referential check (full check happens on resolve())
    recipe_ids = {r.id for r in recipes}
    for qid, rids in quickruns.items():
        for rid in rids:
            if rid not in recipe_ids:
                raise ValidationError(f"quickrun '{qid}' references unknown recipe id: {rid}")

    return CleaningRecipesDoc(vars=vars_map, recipes=recipes, quickruns=quickruns)


def dump_cleaning_recipes(doc: CleaningRecipesDoc) -> Dict[str, Any]:
    return {
        "vars": dict(doc.vars),
        "recipes": [
            {
                "id": r.id,
                "description": r.description,
                "input_default": r.input_default,
                "output_default": r.output_default,
                "keep": list(r.keep or []),
                "rename": dict(r.rename or {}),
                "html_col": r.html_col,
                "meta_cols": list(r.meta_cols or []),
            }
            for r in doc.recipes
        ],
        "quickruns": {k: list(v) for k, v in (doc.quickruns or {}).items()},
    }


RECIPES_LOADER: CatalogLoader[CleaningRecipesDoc] = CatalogLoader(
    app_name="CSVcleaner",
    schema_name=SCHEMA_NAME,
    schema_version=SCHEMA_VERSION,
    validate=validate_cleaning_recipes,
    dump=dump_cleaning_recipes,
)
