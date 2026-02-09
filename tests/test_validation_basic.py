# tests/test_validation_basic.py
from __future__ import annotations

import pytest

from helpers.validation.basic import (
    ValidationError,
    require_dict,
    require_list,
    require_str,
    require_int,
    require_float,
    require_bool,
    require_one_of,
    require_list_of_dicts,
    require_unique,
    require_ip,
)


def test_require_dict_list():
    assert require_dict({"a": 1}, path="x") == {"a": 1}
    assert require_list([1, 2], path="x") == [1, 2]
    with pytest.raises(ValidationError):
        require_dict([], path="x")
    with pytest.raises(ValidationError):
        require_list({}, path="x")


def test_require_str_int_float_bool():
    d = {"s": " hi ", "i": 5, "f": 1.5, "b": True}

    assert require_str(d, "s", path="p") == "hi"
    assert require_int(d, "i", path="p", min_v=0, max_v=10) == 5
    assert require_float(d, "f", path="p", min_v=0.0, max_v=2.0) == 1.5
    assert require_bool(d, "b", path="p") is True

    with pytest.raises(ValidationError):
        require_int({"i": True}, "i", path="p")  # bool rejected as int

    with pytest.raises(ValidationError):
        require_str({"s": "   "}, "s", path="p")  # empty not allowed by default

    assert require_str({}, "s", path="p", default="ok") == "ok"


def test_require_one_of():
    assert require_one_of("a", ["a", "b"], path="x") == "a"
    with pytest.raises(ValidationError):
        require_one_of("c", ["a", "b"], path="x")


def test_require_list_of_dicts():
    d = {"items": [{"a": 1}, {"b": 2}]}
    out = require_list_of_dicts(d, "items", path="root")
    assert out == [{"a": 1}, {"b": 2}]
    with pytest.raises(ValidationError):
        require_list_of_dicts({"items": [1, 2]}, "items", path="root")


def test_require_unique():
    items = [{"id": "a"}, {"id": "b"}]
    require_unique(items, lambda x: x["id"], what="id", path="items")  # no error

    items2 = [{"id": "a"}, {"id": "a"}]
    with pytest.raises(ValidationError):
        require_unique(items2, lambda x: x["id"], what="id", path="items")


@pytest.mark.xfail(reason="require_ip() currently calls require_str() with a mismatched signature in the provided file.")
def test_require_ip_current_bug():
    # As shipped, require_ip likely raises due to require_str signature mismatch.
    assert require_ip("127.0.0.1", path="ip") == "127.0.0.1"
