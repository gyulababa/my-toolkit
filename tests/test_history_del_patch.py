# tests/test_history_del_patch.py

from __future__ import annotations

import pytest

from helpers.history.applier_tree import TreeApplier
from helpers.history.ops import Operation, OpMeta


def test_tree_applier_del_deletes_key_and_inverts_to_set() -> None:
    applier = TreeApplier()

    doc = {"a": {"b": {"c": 123, "d": 456}}}

    op = Operation(
        patch_type="del",
        path=["a", "b", "c"],
        before=123,
        after=None,
        meta=OpMeta(source="test", reason="del"),
    )

    out = applier.apply(doc, op)
    assert "c" not in out["a"]["b"]
    assert out["a"]["b"]["d"] == 456

    inv = applier.invert(op)
    assert inv.patch_type == "set"
    assert inv.path == ["a", "b", "c"]
    assert inv.after == 123

    restored = applier.apply(out, inv)
    assert restored["a"]["b"]["c"] == 123


def test_tree_applier_del_requires_dict_parent() -> None:
    applier = TreeApplier()
    doc = {"a": ["not", "a", "dict"]}

    op = Operation(
        patch_type="del",
        path=["a", 0],  # invalid: last token is not str key, parent is list
        before="not",
        after=None,
        meta=OpMeta(source="test", reason="del"),
    )

    with pytest.raises(Exception):
        applier.apply(doc, op)
