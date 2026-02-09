# tests/persist/test_index.py
# Tests for helpers.persist index lifecycle (ensure_seeded, allocate_next_id, set_active, resolve_doc_id, prune, validate/repair, zip import/export).

from __future__ import annotations

from pathlib import Path

import pytest

from helpers.fs import read_json
from helpers.persist import (
    allocate_next_id,
    ensure_seeded,
    export_domain_zip,
    get_active_path,
    import_domain_zip,
    list_doc_ids,
    prune_docs,
    read_index,
    repair_domain_state,
    resolve_doc_id,
    set_active,
    set_active_latest,
    validate_domain_state,
    write_index,
)
from helpers.persist.types import PersistIndex


def test_ensure_seeded_creates_index_and_seed_doc(tmp_path: Path) -> None:
    """ensure_seeded should create index.json and seed doc if missing."""
    root = tmp_path / "persist"
    ensure_seeded(root, "demo", seed_raw={"hello": "world"})

    idxp = root / "demo" / "index.json"
    docp = root / "demo" / "0001.json"

    assert idxp.exists()
    assert docp.exists()
    assert read_json(docp) == {"hello": "world"}

    idx = read_index(root, "demo")
    assert idx.active_id == "0001"
    assert idx.next_id >= 2


def test_allocate_next_id_monotonic(tmp_path: Path) -> None:
    """allocate_next_id should return padded ids and increment index.next_id."""
    root = tmp_path / "persist"
    ensure_seeded(root, "demo")

    a = allocate_next_id(root, "demo", note="first")
    b = allocate_next_id(root, "demo", note="second")
    assert a == "0002"
    assert b == "0003"

    idx = read_index(root, "demo")
    assert idx.next_id == 4


def test_set_active_and_get_active_path(tmp_path: Path) -> None:
    """set_active should update active_id; get_active_path should reflect it."""
    root = tmp_path / "persist"
    ensure_seeded(root, "demo")

    # Create docs so "0002.json" exists
    new_id = allocate_next_id(root, "demo")
    (root / "demo" / f"{new_id}.json").write_text("{}", encoding="utf-8")

    set_active(root, "demo", new_id, note="activate")
    idx = read_index(root, "demo")
    assert idx.active_id == new_id

    ap = get_active_path(root, "demo")
    assert ap.name == f"{new_id}.json"


def test_resolve_doc_id_selectors(tmp_path: Path) -> None:
    """resolve_doc_id should support active/latest/explicit."""
    root = tmp_path / "persist"
    ensure_seeded(root, "demo")

    # Create 0002 and 0003 doc files
    a = allocate_next_id(root, "demo")
    (root / "demo" / f"{a}.json").write_text("{}", encoding="utf-8")
    b = allocate_next_id(root, "demo")
    (root / "demo" / f"{b}.json").write_text("{}", encoding="utf-8")

    assert resolve_doc_id(root, "demo", "active") == read_index(root, "demo").active_id
    assert resolve_doc_id(root, "demo", "latest") == b
    assert resolve_doc_id(root, "demo", "0002") == "0002"

    with pytest.raises(Exception):
        resolve_doc_id(root, "demo", "not-a-doc")


def test_list_doc_ids_and_prune(tmp_path: Path) -> None:
    """list_doc_ids should list only 4-digit docs; prune_docs should delete older ones."""
    root = tmp_path / "persist"
    ensure_seeded(root, "demo")

    # Seed doc 0001 exists
    for _ in range(5):  # create ids 0002..0006
        doc_id = allocate_next_id(root, "demo")
        (root / "demo" / f"{doc_id}.json").write_text("{}", encoding="utf-8")

    ids = list_doc_ids(root, "demo")
    assert ids[0] == "0001"
    assert ids[-1] == "0006"

    # Keep last 2 docs + active
    deleted = prune_docs(root, "demo", keep_last=2, keep_active=True)
    remaining = set(list_doc_ids(root, "demo"))
    assert "0006" in remaining and "0005" in remaining
    assert read_index(root, "demo").active_id in remaining
    assert all(d not in remaining for d in deleted)


def test_validate_and_repair_domain_state(tmp_path: Path) -> None:
    """validate_domain_state should detect common issues; repair_domain_state should fix them."""
    root = tmp_path / "persist"
    ensure_seeded(root, "demo")

    # Corrupt index: set active to a missing file and next_id too small
    idx = PersistIndex(active_id="9999", next_id=1, history=[])
    write_index(root, "demo", idx)

    rep = validate_domain_state(root, "demo")
    assert not rep.ok
    assert any("Active doc missing" in e for e in rep.errors)

    rep2 = repair_domain_state(root, "demo", ensure_seed_doc=True)
    assert rep2.ok
    idx2 = read_index(root, "demo")
    # After repair, active should point to an existing doc (seed at minimum).
    assert (root / "demo" / f"{idx2.active_id}.json").exists()
    assert idx2.next_id >= 2


def test_export_import_domain_zip(tmp_path: Path) -> None:
    """export_domain_zip/import_domain_zip should round-trip a domain."""
    root = tmp_path / "persist"
    ensure_seeded(root, "demo", seed_raw={"seed": True})

    # Create one more doc
    doc_id = allocate_next_id(root, "demo")
    (root / "demo" / f"{doc_id}.json").write_text('{"x":1}', encoding="utf-8")
    set_active_latest(root, "demo")

    z = tmp_path / "demo.zip"
    export_domain_zip(root, "demo", z, overwrite=True)
    assert z.exists()

    # Import into a new root
    root2 = tmp_path / "persist2"
    imported_domain = import_domain_zip(z, root2, "demo", strategy="merge")
    assert imported_domain == "demo"
    assert (root2 / "demo" / "index.json").exists()
    assert (root2 / "demo" / "0001.json").exists()
