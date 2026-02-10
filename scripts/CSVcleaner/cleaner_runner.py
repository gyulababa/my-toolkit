# scripts/CSVcleaner/cleaner_runner.py
# cleaner_runner.py (patch-style: replace your dataclasses + load_recipes_config, keep the rest)

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from helpers.validation import ValidationError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapters.csvcleaner.recipes import (  # noqa: E402
    CleaningRecipesResolved,
    RecipeResolved,
    load_recipes_resolved,
)
from app.adapters.csvcleaner.run_reports import persist_quickrun_report  # noqa: E402

# Keep your default script logic
CLEANER_SCRIPT_DEFAULT = str(Path(__file__).resolve().parent.parent / "clean_csv_generic.py")


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
    persist_root: Optional[str | Path] = None,
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

    if persist_root:
        persist_quickrun_report(
            persist_root,
            quickrun_id=quickrun_id,
            recipe_ids=list(cfg.quickruns[quickrun_id]),
            results=results,
        )

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
    p_qr.add_argument("--persist-root", default="", help="Persist a run report under this root")

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
                persist_root=args.persist_root.strip() or None,
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
