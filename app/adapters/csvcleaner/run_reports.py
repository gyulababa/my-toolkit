# app/adapters/csvcleaner/run_reports.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

from helpers.catalog import EditableCatalog


def _ensure_scripts_on_path() -> None:
    root = Path(__file__).resolve().parents[3]
    scripts_dir = root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))


_ensure_scripts_on_path()

from CSVcleaner.run_report import CleaningRunReport, RUN_REPORT_PERSIST  # noqa: E402


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
