# cleaner_runner.py (patch-style: replace your dataclasses + load_recipes_config, keep the rest)

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from helpers.catalog import Catalog
from helpers.persist.catalog_loader import CatalogLoader
from helpers.validation import ValidationError


# Keep your default script logic
CLEANER_SCRIPT_DEFAULT = str(Path(__file__).resolve().parent.parent / "clean_csv_generic.py")

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


def load_recipes_resolved(path: str | Path) -> CleaningRecipesResolved:
    """
    Load recipes config through CatalogLoader + Catalog validation, then resolve env overrides and ${VARS}.
    """
    p = Path(path)
    raw = RECIPES_LOADER.load_raw(p)
    cat: Catalog[Any] = Catalog.load(
        raw,
        validate=RECIPES_LOADER.validate,
        schema_name=RECIPES_LOADER.schema_name,
        schema_version=RECIPES_LOADER.schema_version,
    )
    # cat.doc is typed as DocT in your codebase; keep Any here to avoid mypy coupling in scripts
    doc = cat.doc  # type: ignore[attr-defined]
    return doc.resolve(env_prefix="OPS_")


def build_cleaner_args(recipe: RecipeResolved, input_path: str, output_path: str) -> List[str]:
    args = ["--in", input_path, "--out", output_path]

    if recipe.keep:
        args += ["--keep", ",".join(recipe.keep)]

    if recipe.rename:
        args += ["--rename", json.dumps(recipe.rename, ensure_ascii=False)]

    if recipe.html_col:
        args += ["--html-col", recipe.html_col]

    if recipe.meta_cols:
        args += ["--meta-cols", ",".join(recipe.meta_cols)]

    return args


def should_run_default_paths(input_path: str, output_path: str) -> bool:
    ip = Path(input_path)
    if not ip.exists():
        return False
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    return True


async def run_recipe_async(
    recipe: RecipeResolved,
    *,
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    cleaner_script: str = CLEANER_SCRIPT_DEFAULT,
) -> Tuple[int, str, str]:
    in_path = input_path or recipe.input_default
    out_path = output_path or recipe.output_default

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["python", cleaner_script] + build_cleaner_args(recipe, in_path, out_path)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_b, stderr_b = await proc.communicate()
    return proc.returncode, stdout_b.decode("utf-8", "replace"), stderr_b.decode("utf-8", "replace")


async def run_quickrun_async(
    cfg: CleaningRecipesResolved,
    quickrun_id: str,
    *,
    cleaner_script: str = CLEANER_SCRIPT_DEFAULT,
    only_if_defaults_exist: bool = True,
) -> Dict[str, Dict[str, Any]]:
    if quickrun_id not in cfg.quickruns:
        raise KeyError(f"Unknown quickrun id: {quickrun_id}")

    results: Dict[str, Dict[str, Any]] = {}
    for rid in cfg.quickruns[quickrun_id]:
        if rid not in cfg.recipes:
            results[rid] = {"ok": False, "error": "unknown_recipe"}
            continue

        r = cfg.recipes[rid]
        if only_if_defaults_exist and not should_run_default_paths(r.input_default, r.output_default):
            results[rid] = {"ok": False, "skipped": True, "reason": "defaults_missing", "input": r.input_default}
            continue

        code, out, err = await run_recipe_async(r, cleaner_script=cleaner_script)
        results[rid] = {"ok": code == 0, "returncode": code, "stdout": out, "stderr": err}

    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Recipe runner for clean_csv_generic.py (CatalogLoader-backed)")
    ap.add_argument("--recipes", default=str(Path(__file__).with_name("recipes.json")), help="Path to recipes.json")
    ap.add_argument("--cleaner", default=CLEANER_SCRIPT_DEFAULT, help="Path to clean_csv_generic.py")

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List recipes and quickruns")

    p_run = sub.add_parser("run", help="Run a single recipe")
    p_run.add_argument("--id", required=True, help="Recipe id")
    p_run.add_argument("--in", dest="input_path", default="", help="Override input path")
    p_run.add_argument("--out", dest="output_path", default="", help="Override output path")

    p_qr = sub.add_parser("quickrun", help="Run a quickrun")
    p_qr.add_argument("--id", required=True, help="Quickrun id")
    p_qr.add_argument("--force", action="store_true", help="Run even if default input paths missing")

    args = ap.parse_args()

    try:
        cfg = load_recipes_resolved(args.recipes)
    except ValidationError as e:
        print(f"ERROR: invalid recipes config: {e}", file=sys.stderr)
        return 2

    if args.cmd == "list":
        print("Recipes:")
        for rid, r in cfg.recipes.items():
            print(f"  - {rid}: {r.description}")
            print(f"      in : {r.input_default}")
            print(f"      out: {r.output_default}")
        print("\nQuickruns:")
        for qid, rids in cfg.quickruns.items():
            print(f"  - {qid}: {', '.join(rids)}")
        return 0

    if args.cmd == "run":
        rid = args.id
        if rid not in cfg.recipes:
            print(f"ERROR: unknown recipe id: {rid}", file=sys.stderr)
            return 2

        r = cfg.recipes[rid]
        input_path = args.input_path.strip() or None
        output_path = args.output_path.strip() or None

        code, out, err = asyncio.run(run_recipe_async(
            r,
            input_path=input_path,
            output_path=output_path,
            cleaner_script=args.cleaner,
        ))
        if out:
            print(out, end="")
        if err.strip():
            print(err, end="", file=sys.stderr)
        return code

    if args.cmd == "quickrun":
        qid = args.id
        only_if_defaults_exist = not args.force
        try:
            results = asyncio.run(run_quickrun_async(
                cfg,
                qid,
                cleaner_script=args.cleaner,
                only_if_defaults_exist=only_if_defaults_exist,
            ))
        except KeyError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

        ok = sum(1 for v in results.values() if v.get("ok"))
        skip = sum(1 for v in results.values() if v.get("skipped"))
        fail = sum(1 for v in results.values() if (not v.get("ok") and not v.get("skipped")))

        payload = {"ok": ok, "fail": fail, "skip": skip, "results": results}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if fail == 0 else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
