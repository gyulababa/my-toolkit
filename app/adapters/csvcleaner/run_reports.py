# app/adapters/csvcleaner/run_reports.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from helpers.catalog import EditableCatalog

from scripts.CSVcleaner.run_report import CleaningRunReport, RUN_REPORT_PERSIST


def persist_quickrun_report(
    persist_root: str | Path,
    *,
    quickrun_id: str,
    recipe_ids: List[str],
    results: Dict[str, Dict[str, Any]],
) -> Path:
    report = CleaningRunReport(
        tool="cleaner_runner",
        quickrun_id=quickrun_id,
        recipe_ids=list(recipe_ids),
        results=results,
    )
    editable = EditableCatalog.from_catalog(
        report,
        RUN_REPORT_PERSIST.loader.dump,
        schema_name=RUN_REPORT_PERSIST.loader.schema_name,
        schema_version=RUN_REPORT_PERSIST.loader.schema_version,
    )
    return RUN_REPORT_PERSIST.save_new_revision(
        Path(persist_root),
        editable,
        note=f"quickrun:{quickrun_id}",
    )


__all__ = ["persist_quickrun_report"]
