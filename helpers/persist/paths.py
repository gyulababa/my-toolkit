# helpers/persist/paths.py
# Persist-specific path conventions. This is intentionally NOT generic FS logic (that lives in helpers.fs).

from __future__ import annotations

from pathlib import Path


def domain_dir(persist_root: Path, domain: str) -> Path:
    """
    Return the folder path for a persist "domain".

    Layout:
      <persist_root>/<domain>/
    """
    return Path(persist_root).resolve() / domain


def index_path(persist_root: Path, domain: str) -> Path:
    """
    Return the index.json path for a persist domain.

    Layout:
      <persist_root>/<domain>/index.json
    """
    return domain_dir(persist_root, domain) / "index.json"


def doc_path(persist_root: Path, domain: str, doc_id: str) -> Path:
    """
    Return the document path for a persisted doc id.

    Layout:
      <persist_root>/<domain>/<doc_id>.json

    Notes:
      doc_id is typically a 4-digit string like "0001".
    """
    return domain_dir(persist_root, domain) / f"{doc_id}.json"
