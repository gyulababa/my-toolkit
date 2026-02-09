# tests/test_geometry.py
from __future__ import annotations

import pytest

from helpers.geometry import RectF, fit_aspect, clamp_rect_to_bounds


def test_rect_edges_contains():
    r = RectF(10.0, 20.0, 5.0, 7.0)
    assert r.x2 == 15.0
    assert r.y2 == 27.0
    assert r.contains(10.0, 20.0) is True
    assert r.contains(15.0, 27.0) is True  # inclusive edges
    assert r.contains(15.1, 27.0) is False


def test_rect_inset_inflate():
    r = RectF(0.0, 0.0, 10.0, 10.0)
    r2 = r.inset(2.0, 3.0)
    assert r2 == RectF(2.0, 3.0, 6.0, 4.0)

    r3 = r.inflate(1.0, 2.0)
    assert r3 == RectF(-1.0, -2.0, 12.0, 14.0)

    # inset clamps w/h to >= 0
    r4 = r.inset(999.0, 999.0)
    assert r4.w == 0.0
    assert r4.h == 0.0


def test_fit_aspect_contain():
    # src 16:9 into dst 100x100 => letterbox by height
    x, y, w, h = fit_aspect(16, 9, 100, 100, mode="contain")
    assert w == 100
    assert h == 100 / (16 / 9)
    assert x == 0
    assert y > 0


def test_fit_aspect_cover():
    # src 16:9 into dst 100x100 => crop by width
    x, y, w, h = fit_aspect(16, 9, 100, 100, mode="cover")
    assert h == 100
    assert w == 100 * (16 / 9)
    assert y == 0
    assert x < 0


def test_fit_aspect_invalid_dims():
    assert fit_aspect(0, 9, 100, 100) == (0.0, 0.0, 0.0, 0.0)
    assert fit_aspect(16, 9, 0, 100) == (0.0, 0.0, 0.0, 0.0)


def test_clamp_rect_to_bounds():
    bounds = RectF(0.0, 0.0, 100.0, 100.0)
    r = RectF(90.0, 90.0, 20.0, 20.0)
    clamped = clamp_rect_to_bounds(r, bounds)
    assert clamped.x == 80.0
    assert clamped.y == 80.0

    # If rect larger than bounds, pin to bounds origin by policy
    big = RectF(10.0, 20.0, 200.0, 300.0)
    clamped2 = clamp_rect_to_bounds(big, bounds)
    assert clamped2.x == 0.0
    assert clamped2.y == 0.0
