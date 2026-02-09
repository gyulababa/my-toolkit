# helpers/math/basic.py
# Small numeric primitives (clamps, interpolation, remapping, safe math) used broadly across helpers.

from __future__ import annotations

"""
helpers.math.basic
------------------

Small numeric helpers that are safe to use across many projects.

Scope:
- clamps
- interpolation and remapping
- safe division
- rounding helpers
- small easing function (smoothstep)

Non-goals:
- geometry types (see helpers.geometry)
- vector/matrix math
- statistics
"""

from typing import Optional


def clamp(v: float, lo: float, hi: float) -> float:
    """Clamp v into [lo..hi]."""
    return lo if v < lo else hi if v > hi else v


def clamp01(v: float) -> float:
    """Clamp v into [0..1]."""
    return clamp(v, 0.0, 1.0)


def clamp8(v: int) -> int:
    """Clamp integer v into 8-bit unsigned range [0..255]."""
    return int(clamp(int(v), 0, 255))


def clamp_int(v: float, lo: int, hi: int) -> int:
    """Clamp numeric v into [lo..hi], then truncate to int."""
    if lo > hi:
        lo, hi = hi, lo
    return int(clamp(float(v), lo, hi))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b with parameter t in [0..1] (not clamped)."""
    return a + (b - a) * t


def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse lerp: return t such that lerp(a,b,t) ~= v. Returns 0 if a==b."""
    if a == b:
        return 0.0
    return (v - a) / (b - a)


def remap(v: float, in_a: float, in_b: float, out_a: float, out_b: float) -> float:
    """Remap v from range [in_a..in_b] into [out_a..out_b]."""
    t = inv_lerp(in_a, in_b, v)
    return lerp(out_a, out_b, t)


def safe_div(n: float, d: float, *, default: float = 0.0) -> float:
    """Divide n/d, returning default on division by zero."""
    if d == 0:
        return default
    return n / d


def round_int(v: float) -> int:
    """Round a float to nearest int (banker’s rounding depends on Python round())."""
    return int(round(v))


def wrap_index(i: int, n: int) -> int:
    """
    Wrap index i into [0..n-1].

    Useful for cyclic buffers and hue shifts in discrete palettes.
    """
    if n <= 0:
        return 0
    return i % n


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """
    Smoothstep interpolation.

    Returns:
      0 for x<=edge0, 1 for x>=edge1, and a smooth cubic curve in between.
    """
    if edge0 == edge1:
        return 0.0
    t = clamp01((x - edge0) / (edge1 - edge0))
    return t * t * (3 - 2 * t)
