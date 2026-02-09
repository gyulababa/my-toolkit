# cleaning/run_report.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from helpers.persist.catalog_loader import CatalogLoader
from helpers.persist.persisted_catalog_loader import PersistedCatalogLoader
from helpers.validation import ValidationError


@dataclass(frozen=True)
class CleaningRunReport:
    tool: str
    quickrun_id: Optional[str]
    recipe_ids: List[str]
    results: Dict[str, Dict[str, Any]]  # per recipe: ok/returncode/stdout/stderr/skipped/etc.


def validate_run_report(raw: Dict[str, Any]) -> CleaningRunReport:
    if not isinstance(raw, dict):
        raise ValidationError("Doc must be an object")

    tool = str(raw.get("tool") or "").strip()
    if not tool:
        raise ValidationError("tool must be non-empty")

    quickrun_id = raw.get("quickrun_id")
    if quickrun_id is not None:
        quickrun_id = str(quickrun_id)

    recipe_ids_raw = raw.get("recipe_ids") or []
    if not isinstance(recipe_ids_raw, list):
        raise ValidationError("recipe_ids must be a list")

    results = raw.get("results") or {}
    if not isinstance(results, dict):
        raise ValidationError("results must be an object")

    return CleaningRunReport(
        tool=tool,
        quickrun_id=quickrun_id,
        recipe_ids=[str(x) for x in recipe_ids_raw],
        results=results,
    )


def dump_run_report(doc: CleaningRunReport) -> Dict[str, Any]:
    return {
        "tool": doc.tool,
        "quickrun_id": doc.quickrun_id,
        "recipe_ids": list(doc.recipe_ids),
        "results": doc.results,
    }


RUN_REPORT_LOADER: CatalogLoader[CleaningRunReport] = CatalogLoader(
    app_name="CSVcleaner",
    schema_name="cleaning_run_report",
    schema_version=1,
    validate=validate_run_report,
    dump=dump_run_report,
)

RUN_REPORT_PERSIST: PersistedCatalogLoader[CleaningRunReport] = PersistedCatalogLoader(
    loader=RUN_REPORT_LOADER,
    domain="cleaning_runs",
    seed_raw=lambda: {
        "tool": "cleaner_runner",
        "quickrun_id": None,
        "recipe_ids": [],
        "results": {},
    },
)
