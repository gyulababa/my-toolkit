from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from scripts.CSVcleaner.cleaner_runner import load_recipes_config, run_quickrun_async
from app.sqlite.dbkit import default_db_config, open_db, SqliteDocStore, DocKey


# -----------------------------
# Config
# -----------------------------

@dataclass(frozen=True)
class RefreshPaths:
    data_dir: Path
    inbox_dir: Path
    db_path: Path
    recipes_path: Path
    index_sources_path: Path
    index_settings_path: Optional[Path]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _apply_overrides(index_cfg: Dict[str, Any], settings_cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not settings_cfg:
        return index_cfg
    overrides = settings_cfg.get("overrides") or {}
    for s in index_cfg.get("sources") or []:
        sid = s.get("id")
        if sid in overrides:
            for k, v in overrides[sid].items():
                # supports "index.fields" and "display.fields"
                if k == "index.fields":
                    s.setdefault("index", {})["fields"] = v
                elif k == "display.fields":
                    s.setdefault("display", {})["fields"] = v
    return index_cfg


# -----------------------------
# Fetch (manual inbox copy)
# -----------------------------

def fetch_from_inbox(inbox_dir: Path, raw_dir: Path, mapping: Dict[str, str]) -> None:
    """
    mapping: { "inbox_filename.csv": "relative/raw/target.csv" }
    """
    raw_dir.mkdir(parents=True, exist_ok=True)

    for inbox_name, rel_target in mapping.items():
        src = inbox_dir / inbox_name
        if not src.exists():
            raise FileNotFoundError(f"Missing in inbox: {src}")
        dst = raw_dir / rel_target
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


# -----------------------------
# Projection helpers
# -----------------------------

def _get_col(row: pd.Series, col: str) -> str:
    if col not in row.index:
        return ""
    v = row[col]
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none") else s


def _project_field(spec: Dict[str, Any], row: pd.Series) -> str:
    if "literal" in spec:
        return str(spec["literal"])
    if "col" in spec:
        v = _get_col(row, spec["col"])
        if v:
            return v
        for fb in spec.get("fallback_cols") or []:
            v2 = _get_col(row, fb)
            if v2:
                return v2
        return ""
    if "join_cols" in spec:
        parts = []
        for c in spec["join_cols"]:
            v = _get_col(row, c)
            if v:
                parts.append(v)
            elif not spec.get("skip_empty", False):
                parts.append("")
        sep = str(spec.get("sep") or "\n")
        joined = sep.join([p for p in parts if p or not spec.get("skip_empty", False)])
        return joined.strip()
    return ""


def build_canonical_doc(source_id: str, proj: Dict[str, Any], row: pd.Series) -> Dict[str, str]:
    doc_id = _project_field(proj["doc_id"], row)
    title = _project_field(proj["title"], row)
    body = _project_field(proj["body"], row)
    tags = _project_field(proj["tags"], row)
    ag = _project_field(proj["assignment_group"], row)

    # meta: keep minimal provenance
    meta = {
        "source_id": source_id,
        "source_row": _project_field(proj.get("source_row", {"literal": ""}), row),
    }

    return {
        "kind": "kb",
        "doc_id": f"{source_id}:{doc_id}" if source_id != "kb" else doc_id,
        "title": title,
        "body": body,
        "tags": tags,
        "assignment_group": ag,
        "meta_json": json.dumps(meta, ensure_ascii=False),
    }


# -----------------------------
# DB rebuild + import
# -----------------------------

def purge_db(db_path: Path, backups_dir: Path, keep_backup: bool) -> None:
    if not db_path.exists():
        return
    backups_dir.mkdir(parents=True, exist_ok=True)
    if keep_backup:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.move(str(db_path), str(backups_dir / f"ops_{stamp}.db"))
    else:
        db_path.unlink()


def import_sources_to_sqlite(db_path: Path, index_cfg: Dict[str, Any]) -> None:
    # Force dbkit to use this db path
    # (or pass explicit DbConfig; keeping simple)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = open_db(default_db_config().__class__(path=db_path))  # type: ignore
    store = SqliteDocStore(conn)

    # Create schema fresh
    # (migrate_if_needed reads schema.sql; make sure it's in place)
    store.migrate_if_needed()

    # Bulk insert in one transaction
    conn.execute("BEGIN;")
    try:
        for src in index_cfg["sources"]:
            source_id = src["id"]
            clean_path = Path(src["clean_path"])
            if not clean_path.exists():
                continue

            df = pd.read_csv(clean_path, dtype=str, keep_default_na=False)
            proj = src["projection"]

            for _, row in df.iterrows():
                doc = build_canonical_doc(source_id, proj, row)
                key = DocKey(kind=doc["kind"], doc_id=doc["doc_id"])

                # Create-or-replace strategy for weekly rebuild:
                # since DB is purged, this is always create.
                store.create_doc(
                    key,
                    title=doc["title"],
                    body=doc["body"],
                    tags=doc["tags"],
                    assignment_group=doc["assignment_group"],
                    meta=json.loads(doc["meta_json"]),
                    note=f"import:{source_id}",
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# -----------------------------
# Backup + delete helpers
# -----------------------------

def _ts_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_inbox_files(inbox_dir: Path, backup_root: Path, filenames: List[str]) -> Path:
    stamp = _ts_slug()
    dest_dir = backup_root / stamp
    dest_dir.mkdir(parents=True, exist_ok=True)

    for name in filenames:
        src = inbox_dir / name
        if src.exists():
            shutil.copy2(src, dest_dir / name)
    return dest_dir


def delete_inbox_files(inbox_dir: Path, filenames: List[str]) -> None:
    for name in filenames:
        p = inbox_dir / name
        if p.exists():
            p.unlink()


# -----------------------------
# Main
# -----------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly refresh: fetch raw CSVs -> clean -> rebuild SQLite + FTS")
    ap.add_argument("--data-dir", default="./data")
    ap.add_argument("--inbox-dir", default="./inbox")
    ap.add_argument("--db", default="./data/ops.db")
    ap.add_argument("--recipes", default="./cleaning/recipes.json")
    ap.add_argument("--index-sources", default="./index_sources.json")
    ap.add_argument("--index-settings", default="./index_settings.json")
    ap.add_argument("--no-index-settings", action="store_true")
    ap.add_argument("--no-backup", action="store_true", help="Delete DB instead of backing up.")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--skip-clean", action="store_true")
    ap.add_argument("--skip-import", action="store_true")
    ap.add_argument("--backup-inbox", action="store_true", help="Backup inbox CSVs after successful processing.")
    ap.add_argument("--delete-inbox", action="store_true", help="Delete inbox CSVs after backup (requires --backup-inbox).")
    ap.add_argument("--inbox-backup-dir", default="./inbox_backups", help="Where to store timestamped inbox backups.")

    args = ap.parse_args()

    paths = RefreshPaths(
        data_dir=Path(args.data_dir),
        inbox_dir=Path(args.inbox_dir),
        db_path=Path(args.db),
        recipes_path=Path(args.recipes),
        index_sources_path=Path(args.index_sources),
        index_settings_path=None if args.no_index_settings else Path(args.index_settings),
    )

    # 1) Fetch
    if not args.skip_fetch:
        mapping = {
            # inbox filename -> raw relative target (must match recipes.json defaults)
            "kb_knowledge.csv": "kb/kb_knowledge.csv",
            "Support Spektrum(ART).csv": "spektrum/spektrum_art.csv",
            "Support Spektrum(SAP Buzzwords).csv": "spektrum/spektrum_sap_buzzwords.csv",
        }
        inbox_files_used = list(mapping.keys())

        fetch_from_inbox(paths.inbox_dir, paths.data_dir / "raw", mapping)

    # 2) Clean (recipes quickrun)
    if not args.skip_clean:
        cfg = load_recipes_config(paths.recipes_path)
        # run "kb_all" quickrun; force=False means skip missing defaults
        res = asyncio_run(run_quickrun_async(cfg, "kb_all"))  # see helper below
        # optional: check failures
        for rid, rr in res.items():
            if rr.get("skipped"):
                continue
            if not rr.get("ok"):
                raise RuntimeError(f"Clean failed: {rid}")

    if args.backup_inbox or args.delete_inbox:
        backup_root = Path(args.inbox_backup_dir)
        backup_dir = backup_inbox_files(paths.inbox_dir, backup_root, inbox_files_used)
        print(f"[inbox] backed up to: {backup_dir}")

        if args.delete_inbox:
            if not args.backup_inbox:
                raise RuntimeError("--delete-inbox requires --backup-inbox (backup must happen first).")
            delete_inbox_files(paths.inbox_dir, inbox_files_used)
            print("[inbox] deleted processed files")


    # 3) Purge DB
    if not args.skip_import:
        purge_db(paths.db_path, paths.data_dir / "backups", keep_backup=not args.no_backup)

        index_cfg = _load_json(paths.index_sources_path)
        settings_cfg = None
        if paths.index_settings_path and paths.index_settings_path.exists():
            settings_cfg = _load_json(paths.index_settings_path)
        index_cfg = _apply_overrides(index_cfg, settings_cfg)

        import_sources_to_sqlite(paths.db_path, index_cfg)

    return 0


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    raise SystemExit(main())
