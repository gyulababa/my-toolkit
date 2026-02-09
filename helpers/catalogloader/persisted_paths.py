# helpers/catalogloader/persisted_paths.py
from __future__ import annotations

from pathlib import Path

from helpers.fs.paths import join_safe


def domain_root(persist_root: Path, domain: str) -> Path:
    return join_safe(persist_root, domain)


def index_path(persist_root: Path, domain: str) -> Path:
    return join_safe(domain_root(persist_root, domain), "index.json")


def docs_root(persist_root: Path, domain: str) -> Path:
    """
    Root directory for persisted docs.

    Current layout stores doc revisions directly under <persist_root>/<domain>/.
    """
    return domain_root(persist_root, domain)


def doc_dir(persist_root: Path, domain: str, doc_id: str) -> Path:
    """
    Directory for a specific doc_id if the layout uses per-doc folders.

    Note: current layout does not use per-doc folders; this returns docs_root.
    """
    _ = doc_id
    return docs_root(persist_root, domain)


def revisions_dir(persist_root: Path, domain: str, doc_id: str) -> Path:
    """
    Directory for revisions for a specific doc_id.

    Note: current layout stores revisions as files in the domain root.
    """
    _ = doc_id
    return domain_root(persist_root, domain)


def doc_path(persist_root: Path, domain: str, doc_id: str) -> Path:
    return join_safe(domain_root(persist_root, domain), f"{doc_id}.json")


def revision_path(persist_root: Path, domain: str, doc_id: str) -> Path:
    return doc_path(persist_root, domain, doc_id)
