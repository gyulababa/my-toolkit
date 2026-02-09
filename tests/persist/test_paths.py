# tests/persist/test_paths.py
# Tests for helpers.persist path conventions (domain_dir, index_path, doc_path).

from __future__ import annotations

from pathlib import Path

from helpers.persist import doc_path, domain_dir, index_path


def test_paths_shapes(tmp_path: Path) -> None:
    """Persist path helpers should produce predictable paths under persist_root/domain."""
    root = tmp_path / "persist"
    domain = "kb"

    dd = domain_dir(root, domain)
    ip = index_path(root, domain)
    dp = doc_path(root, domain, "0007")

    assert dd == root.resolve() / domain
    assert ip == root.resolve() / domain / "index.json"
    assert dp == root.resolve() / domain / "0007.json"
