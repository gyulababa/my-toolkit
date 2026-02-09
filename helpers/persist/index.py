# helpers/persist/index.py
# Persist index operations: domain layout, index/doc lifecycle, revisioning, inventory, prune, validation/repair, and packaging.
# This module intentionally delegates generic IO (JSON, atomic writes, directories, deletes, copy/move) to helpers.fs.

from __future__ import annotations

import os
import time
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from helpers.fs import (
    ensure_dir,
    read_json_default,
    read_json_strict,
    atomic_write_json,
    rm,
    rmdir,
    copy_file,
)
from helpers.time_utils import utc_now_iso
from helpers.validation.basic import ValidationError

from .paths import domain_dir, index_path, doc_path
from .types import PersistDocInfo, PersistDomainReport, PersistHistoryEntry, PersistIndex


def _parse_doc_id(stem: str) -> Optional[int]:
    """
    Parse a 4-digit doc id stem into an int. Returns None if invalid.

    Examples:
      "0001" -> 1
      "12"   -> None
      "abcd" -> None
    """
    if len(stem) == 4 and stem.isdigit():
        return int(stem)
    return None


@contextmanager
def with_domain_lock(
    persist_root: Path,
    domain: str,
    *,
    timeout_seconds: float = 10.0,
    poll_interval_seconds: float = 0.1,
) -> Iterable[None]:
    """
    Cooperative lock for domain updates (index/doc writes).

    Implementation:
      Creates <domain>/.lock using O_EXCL. On exit, removes it.

    Why:
      Atomic writes prevent corrupted files, but they do not prevent logical races
      (e.g. two processes allocating the same next_id). This lock reduces that risk.
    """
    d = domain_dir(persist_root, domain)
    ensure_dir(d)
    lock_path = d / ".lock"

    start = time.monotonic()
    fd: Optional[int] = None

    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"pid={os.getpid()} utc={utc_now_iso()}\n".encode("utf-8"))
            os.close(fd)
            fd = None
            break
        except FileExistsError:
            if time.monotonic() - start >= timeout_seconds:
                raise TimeoutError(f"Timed out waiting for domain lock: {lock_path}")
            time.sleep(poll_interval_seconds)

    try:
        yield
    finally:
        try:
            rm(lock_path, missing_ok=True)
        except Exception:
            # Best-effort: lockfile should not crash caller on cleanup failure.
            pass


def ensure_domain(persist_root: Path, domain: str) -> Path:
    """
    Ensure the domain directory exists and return its path.

    Layout:
      <persist_root>/<domain>/
    """
    d = domain_dir(persist_root, domain)
    ensure_dir(d)
    return d


def read_index(persist_root: Path, domain: str) -> PersistIndex:
    """
    Read <domain>/index.json and return PersistIndex.

    If index.json is missing, returns a default PersistIndex.
    """
    p = index_path(persist_root, domain)
    if not p.exists():
        return PersistIndex()

    try:
        raw = read_json_strict(p, root_types=(dict,))
    except Exception as e:
        raise ValidationError(f"Failed to load persist index JSON: {p}") from e

    try:
        return PersistIndex.from_raw(raw)
    except Exception as e:
        raise ValidationError(f"Failed to parse PersistIndex: {p}") from e


def write_index(persist_root: Path, domain: str, index: PersistIndex, *, indent: int = 2) -> None:
    """
    Atomically write PersistIndex to <domain>/index.json.

    Uses helpers.fs.atomic_write_json to reduce risk of partial writes.
    """
    p = index_path(persist_root, domain)
    atomic_write_json(p, index.to_raw(), indent=indent, sort_keys=True)


def update_index(
    persist_root: Path,
    domain: str,
    mutator: Callable[[PersistIndex], PersistIndex] | Callable[[PersistIndex], None],
    *,
    indent: int = 2,
) -> PersistIndex:
    """
    Transaction-style index update: read -> mutate -> atomic write.

    mutator may:
      - mutate the PersistIndex in-place and return None, OR
      - return a new PersistIndex instance

    Returns:
      The updated PersistIndex.
    """
    ensure_domain(persist_root, domain)
    with with_domain_lock(persist_root, domain):
        idx = read_index(persist_root, domain)
        res = mutator(idx)
        if res is not None:
            idx = res
        write_index(persist_root, domain, idx, indent=indent)
        return idx


def list_doc_ids(persist_root: Path, domain: str) -> List[str]:
    """
    Return all persisted document ids found in the domain folder (sorted).

    Recognizes:
      - 0001.json, 0002.json, ...
    Ignores:
      - index.json
      - non-4-digit stems
    """
    d = domain_dir(persist_root, domain)
    if not d.exists():
        return []

    ids: List[str] = []
    for p in d.glob("*.json"):
        if p.name == "index.json":
            continue
        if _parse_doc_id(p.stem) is not None:
            ids.append(p.stem)
    return sorted(ids)


def get_active_path(persist_root: Path, domain: str) -> Path:
    """Return the path to the active doc (<domain>/<active_id>.json)."""
    idx = read_index(persist_root, domain)
    return doc_path(persist_root, domain, idx.active_id)


def resolve_doc_id(persist_root: Path, domain: str, selector: str) -> str:
    """
    Resolve common selectors into a concrete doc_id.

    Supported selectors:
      - "active": index.active_id
      - "latest": highest existing 4-digit id (falls back to index.active_id if none exist)
      - "0007": explicit 4-digit id (validated for format only)
    """
    s = selector.strip().lower()
    if s == "active":
        return read_index(persist_root, domain).active_id
    if s == "latest":
        ids = list_doc_ids(persist_root, domain)
        if ids:
            return ids[-1]
        return read_index(persist_root, domain).active_id

    # Explicit id
    if _parse_doc_id(selector) is None:
        raise ValidationError(f"Invalid doc selector/id: {selector!r}")
    return selector


def _doc_note_from_history(idx: PersistIndex, doc_id: str) -> Optional[str]:
    """Return the most recent note for a doc_id from history (best-effort)."""
    for h in reversed(idx.history):
        if h.doc_id == doc_id and h.note:
            return h.note
    return None


def get_doc_info(persist_root: Path, domain: str, doc_id: str) -> PersistDocInfo:
    """
    Return PersistDocInfo (metadata) for a specific doc id.

    Raises:
      ValidationError if the doc does not exist.
    """
    ensure_domain(persist_root, domain)
    idx = read_index(persist_root, domain)
    p = doc_path(persist_root, domain, doc_id)
    if not p.exists():
        raise ValidationError(f"Missing persisted doc: {p}")

    st = p.stat()
    mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    return PersistDocInfo(
        doc_id=doc_id,
        path=str(p),
        is_active=(doc_id == idx.active_id),
        mtime_iso=mtime,
        size_bytes=int(st.st_size),
        note=_doc_note_from_history(idx, doc_id),
    )


def list_docs(persist_root: Path, domain: str) -> List[PersistDocInfo]:
    """
    List all docs in a domain with basic metadata (sorted by doc id).

    Intended for UIs and tooling.
    """
    ensure_domain(persist_root, domain)
    idx = read_index(persist_root, domain)
    infos: List[PersistDocInfo] = []

    for doc_id in list_doc_ids(persist_root, domain):
        p = doc_path(persist_root, domain, doc_id)
        try:
            st = p.stat()
            mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            infos.append(
                PersistDocInfo(
                    doc_id=doc_id,
                    path=str(p),
                    is_active=(doc_id == idx.active_id),
                    mtime_iso=mtime,
                    size_bytes=int(st.st_size),
                    note=_doc_note_from_history(idx, doc_id),
                )
            )
        except FileNotFoundError:
            # Raced deletion; skip best-effort.
            continue

    return infos


def allocate_next_id(persist_root: Path, domain: str, *, note: Optional[str] = None) -> str:
    """
    Allocate a new 4-digit doc id and advance index.next_id.

    Does not write the doc itself; only updates the index.

    Returns:
      doc_id like "0003"
    """
    ensure_domain(persist_root, domain)

    with with_domain_lock(persist_root, domain):
        idx = read_index(persist_root, domain)
        doc_id = f"{idx.next_id:04d}"
        idx.next_id += 1
        if note is not None:
            idx.history.append(PersistHistoryEntry(doc_id=doc_id, created_at=utc_now_iso(), note=note))
        write_index(persist_root, domain, idx)
        return doc_id


def set_active(persist_root: Path, domain: str, doc_id: str, *, note: Optional[str] = None) -> None:
    """Set active_id in <domain>/index.json."""
    ensure_domain(persist_root, domain)

    def _mut(idx: PersistIndex) -> None:
        idx.active_id = str(doc_id)
        if note is not None:
            idx.history.append(PersistHistoryEntry(doc_id=str(doc_id), created_at=utc_now_iso(), note=note))

    update_index(persist_root, domain, _mut)


def set_active_latest(persist_root: Path, domain: str, *, note: Optional[str] = None) -> str:
    """
    Set active_id to the highest existing doc id.

    Returns:
      The doc_id that was set active.
    """
    ensure_domain(persist_root, domain)
    latest = resolve_doc_id(persist_root, domain, "latest")
    set_active(persist_root, domain, latest, note=note or "set active to latest")
    return latest


def ensure_seeded(
    persist_root: Path,
    domain: str,
    *,
    seed_doc_id: str = "0001",
    seed_raw: Optional[Dict[str, Any]] = None,
    indent: int = 2,
) -> None:
    """
    Ensure a domain folder has:
      - index.json
      - seed_doc_id.json (default "0001.json")

    If seed_raw is None, creates an empty JSON object {}.

    This function is intentionally domain-agnostic: it does not validate the doc,
    it only ensures the basic persisted structure exists.
    """
    ensure_domain(persist_root, domain)
    idxp = index_path(persist_root, domain)
    docp = doc_path(persist_root, domain, seed_doc_id)

    with with_domain_lock(persist_root, domain):
        # Seed index.json
        if not idxp.exists():
            idx = PersistIndex(active_id=seed_doc_id, next_id=2)
            write_index(persist_root, domain, idx, indent=indent)

        # Seed the first document
        if not docp.exists():
            raw = seed_raw if seed_raw is not None else {}
            atomic_write_json(docp, raw, indent=indent, sort_keys=True)


def prune_docs(
    persist_root: Path,
    domain: str,
    *,
    keep_last: int = 20,
    keep_active: bool = True,
) -> List[str]:
    """
    Delete older persisted docs to avoid unbounded growth.

    Args:
      keep_last: keep the newest N docs by id.
      keep_active: if True, always keep the active doc even if it is old.

    Returns:
      List of doc_ids that were deleted.
    """
    ensure_domain(persist_root, domain)
    idx = read_index(persist_root, domain)

    ids = list_doc_ids(persist_root, domain)
    if keep_last <= 0:
        keep_set = set()
    else:
        keep_set = set(ids[-keep_last:])

    if keep_active:
        keep_set.add(idx.active_id)

    deleted: List[str] = []
    for doc_id in ids:
        if doc_id in keep_set:
            continue
        p = doc_path(persist_root, domain, doc_id)
        if p.exists():
            rm(p, missing_ok=True)
            deleted.append(doc_id)

    return deleted


def validate_domain_state(persist_root: Path, domain: str) -> PersistDomainReport:
    """
    Validate domain integrity and return a structured report (no exceptions for common issues).

    Checks:
      - index.json exists and is readable (or warns if missing)
      - active doc exists
      - doc ids are well-formed
      - next_id is consistent with existing docs (warn if not)
    """
    report = PersistDomainReport()
    d = domain_dir(persist_root, domain)

    report.stats["domain_dir"] = str(d)
    report.stats["domain_exists"] = d.exists()

    if not d.exists():
        report.errors.append(f"Missing domain directory: {d}")
        return report

    idxp = index_path(persist_root, domain)
    report.stats["index_path"] = str(idxp)

    if not idxp.exists():
        report.warnings.append(f"Missing index.json: {idxp}")
        idx = PersistIndex()
    else:
        try:
            idx = read_index(persist_root, domain)
        except Exception as e:
            report.errors.append(f"Index load failed: {idxp} ({e})")
            return report

    report.stats["active_id"] = idx.active_id
    report.stats["next_id"] = idx.next_id

    # Doc inventory
    ids = list_doc_ids(persist_root, domain)
    report.stats["doc_count"] = len(ids)
    report.stats["max_doc_id"] = ids[-1] if ids else None

    # Active exists?
    ap = doc_path(persist_root, domain, idx.active_id)
    if not ap.exists():
        report.errors.append(f"Active doc missing: {ap}")

    # next_id consistency (best-effort)
    if ids:
        max_id_int = max(int(x) for x in ids)
        expected_next = max_id_int + 1
        if idx.next_id < expected_next:
            report.warnings.append(f"next_id too small: next_id={idx.next_id}, expected>={expected_next}")
        # If next_id is much larger, it is not an error, but worth noting.
        if idx.next_id > expected_next + 1000:
            report.warnings.append(f"next_id unusually large: next_id={idx.next_id}, expected~={expected_next}")

    return report


def repair_domain_state(
    persist_root: Path,
    domain: str,
    *,
    ensure_seed_doc: bool = True,
    indent: int = 2,
) -> PersistDomainReport:
    """
    Repair common domain issues in-place, then return the post-repair report.

    Repairs:
      - create missing index.json (default PersistIndex)
      - if active doc missing and docs exist -> set active to latest
      - if next_id < max(existing)+1 -> set next_id accordingly
      - optionally ensure seed doc exists (0001.json) if no docs exist

    Returns:
      Post-repair PersistDomainReport.
    """
    ensure_domain(persist_root, domain)

    def _repair(idx: PersistIndex) -> PersistIndex:
        ids = list_doc_ids(persist_root, domain)

        # Ensure there's at least one doc if requested.
        if ensure_seed_doc and not ids:
            seedp = doc_path(persist_root, domain, "0001")
            if not seedp.exists():
                atomic_write_json(seedp, {}, indent=indent, sort_keys=True)
            ids = list_doc_ids(persist_root, domain)

        # Fix active to latest if missing.
        active_path = doc_path(persist_root, domain, idx.active_id)
        if not active_path.exists() and ids:
            idx.active_id = ids[-1]
            idx.history.append(PersistHistoryEntry(doc_id=idx.active_id, created_at=utc_now_iso(), note="repair: set active to latest"))

        # Fix next_id monotonicity.
        if ids:
            max_id_int = max(int(x) for x in ids)
            expected_next = max_id_int + 1
            if idx.next_id < expected_next:
                idx.next_id = expected_next
                idx.history.append(PersistHistoryEntry(doc_id=idx.active_id, created_at=utc_now_iso(), note=f"repair: set next_id={expected_next}"))

        return idx

    # Ensure index exists by forcing a write if missing.
    idxp = index_path(persist_root, domain)
    if not idxp.exists():
        write_index(persist_root, domain, PersistIndex(), indent=indent)

    update_index(persist_root, domain, _repair, indent=indent)
    return validate_domain_state(persist_root, domain)


def copy_domain(
    persist_root: Path,
    domain: str,
    dst_root: Path,
    *,
    include_docs: bool = True,
    overwrite: bool = False,
) -> Path:
    """
    Copy a persist domain to another persist root.

    Copies:
      - index.json always (if present)
      - docs (*.json excluding index.json) if include_docs=True

    Args:
      overwrite: if False and destination exists, raises FileExistsError.

    Returns:
      Destination domain directory path.
    """
    src_dir = domain_dir(persist_root, domain)
    dst_dir = domain_dir(dst_root, domain)

    if dst_dir.exists():
        if not overwrite:
            raise FileExistsError(str(dst_dir))
        rmdir(dst_dir, recursive=True, missing_ok=True)

    ensure_dir(dst_dir)

    # Copy index.json if present.
    src_index = index_path(persist_root, domain)
    if src_index.exists():
        copy_file(src_index, index_path(dst_root, domain), overwrite=True, preserve_metadata=True)

    if include_docs and src_dir.exists():
        for p in src_dir.glob("*.json"):
            if p.name == "index.json":
                continue
            if _parse_doc_id(p.stem) is None:
                continue
            copy_file(p, dst_dir / p.name, overwrite=True, preserve_metadata=True)

    return dst_dir


def export_domain_zip(persist_root: Path, domain: str, zip_path: Path, *, overwrite: bool = True) -> Path:
    """
    Export a domain folder (index + docs) into a zip archive.

    The archive layout includes the domain folder as the top-level prefix.
    """
    src_dir = domain_dir(persist_root, domain)
    if not src_dir.exists():
        raise FileNotFoundError(str(src_dir))

    if zip_path.exists() and not overwrite:
        raise FileExistsError(str(zip_path))

    ensure_dir(zip_path.parent)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in src_dir.rglob("*"):
            if p.is_dir():
                continue
            arcname = str(Path(domain) / p.relative_to(src_dir))
            zf.write(p, arcname=arcname)

    return zip_path


def import_domain_zip(
    zip_path: Path,
    persist_root: Path,
    domain: str,
    *,
    strategy: str = "merge",
) -> str:
    """
    Import a domain zip created by export_domain_zip().

    Args:
      strategy:
        - "merge": extract over existing domain (files may overwrite)
        - "replace": delete existing domain dir then extract
        - "new-domain": if domain exists, import into domain_1, domain_2, ...

    Returns:
      The domain name that was imported into (may differ when strategy="new-domain").
    """
    if not zip_path.exists():
        raise FileNotFoundError(str(zip_path))

    ensure_dir(persist_root)
    target_domain = domain
    target_dir = domain_dir(persist_root, target_domain)

    if strategy not in {"merge", "replace", "new-domain"}:
        raise ValueError(f"Invalid import strategy: {strategy!r}")

    if strategy == "new-domain":
        if target_dir.exists():
            i = 1
            while True:
                cand = f"{domain}_{i}"
                cand_dir = domain_dir(persist_root, cand)
                if not cand_dir.exists():
                    target_domain = cand
                    target_dir = cand_dir
                    break
                i += 1

    if strategy == "replace" and target_dir.exists():
        rmdir(target_dir, recursive=True, missing_ok=True)

    ensure_dir(target_dir)

    with zipfile.ZipFile(zip_path, "r") as zf:
        # We expect files under "<domain>/*". We extract only that subtree.
        prefix = f"{domain}/"
        members = [m for m in zf.namelist() if m.startswith(prefix) and not m.endswith("/")]
        for m in members:
            rel = m[len(prefix) :]
            out = target_dir / rel
            ensure_dir(out.parent)
            with zf.open(m) as src, open(out, "wb") as dst:
                dst.write(src.read())

    return target_domain
