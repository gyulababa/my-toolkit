# helpers/catalogloader/persisted_paths.py
# Deprecated facade. Use helpers.persist.paths instead.

from __future__ import annotations

from pathlib import Path

from helpers.persist.paths import domain_dir, index_path, doc_path

__all__ = [
    "domain_root",
    "index_path",
    "docs_root",
    "doc_dir",
    "revisions_dir",
    "doc_path",
    "revision_path",
]


def domain_root(persist_root: Path, domain: str) -> Path:
    return domain_dir(persist_root, domain)


def docs_root(persist_root: Path, domain: str) -> Path:
    return domain_dir(persist_root, domain)


def doc_dir(persist_root: Path, domain: str, doc_id: str) -> Path:
    _ = doc_id
    return docs_root(persist_root, domain)


def revisions_dir(persist_root: Path, domain: str, doc_id: str) -> Path:
    _ = doc_id
    return domain_dir(persist_root, domain)


def revision_path(persist_root: Path, domain: str, doc_id: str) -> Path:
    return doc_path(persist_root, domain, doc_id)
