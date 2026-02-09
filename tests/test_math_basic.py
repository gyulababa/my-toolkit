# tests/test_math_basic.py
from __future__ import annotations

import math
import pytest

from helpers.math.basic import (
    clamp,
    clamp01,
    clamp8,
    clamp_int,
    lerp,
    inv_lerp,
    remap,
    safe_div,
    round_int,
    wrap_index,
    smoothstep,
)


def test_clamp_basic():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(999, 0, 10) == 10


def test_clamp01():
    assert clamp01(-0.1) == 0.0
    assert clamp01(0.5) == 0.5
    assert clamp01(2.0) == 1.0


def test_clamp8():
    assert clamp8(-1) == 0
    assert clamp8(0) == 0
    assert clamp8(255) == 255
    assert clamp8(256) == 255


def test_clamp_int():
    assert clamp_int(-100.0, 0, 10) == 0
    assert clamp_int(5.9, 0, 10) == 5  # truncation after clamp
    assert clamp_int(11.0, 0, 10) == 10
    # swapped bounds defensive
    assert clamp_int(2.0, 10, 0) == 2


def test_lerp_inv_lerp_remap():
    assert lerp(0.0, 10.0, 0.5) == 5.0
    assert inv_lerp(0.0, 10.0, 0.0) == 0.0
    assert inv_lerp(0.0, 10.0, 10.0) == 1.0
    assert inv_lerp(0.0, 10.0, 5.0) == 0.5

    # a == b -> inv_lerp returns 0.0 by policy
    assert inv_lerp(1.0, 1.0, 999.0) == 0.0

    assert remap(5.0, 0.0, 10.0, 0.0, 100.0) == 50.0


def test_safe_div():
    assert safe_div(10.0, 2.0) == 5.0
    assert safe_div(10.0, 0.0, default=123.0) == 123.0


def test_round_int():
    assert round_int(1.2) == 1
    assert round_int(1.5) == 2
    assert round_int(-1.2) == -1
    assert round_int(-1.5) == -2


def test_wrap_index():
    assert wrap_index(0, 5) == 0
    assert wrap_index(4, 5) == 4
    assert wrap_index(5, 5) == 0
    assert wrap_index(-1, 5) == 4
    assert wrap_index(123, 0) == 0  # defensive


def test_smoothstep():
    assert smoothstep(0.0, 1.0, -1.0) == 0.0
    assert smoothstep(0.0, 1.0, 2.0) == 1.0
    mid = smoothstep(0.0, 1.0, 0.5)
    assert 0.0 < mid < 1.0
    assert math.isclose(mid, 0.5, rel_tol=0.0, abs_tol=1e-9)
