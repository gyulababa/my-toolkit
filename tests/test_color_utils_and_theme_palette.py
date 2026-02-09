# tests/test_color_utils_and_theme_palette.py
from __future__ import annotations

import pytest

from helpers.color.color_utils import (
    rgb_to_hsv,
    hsv_to_rgb,
    blend_rgb,
    relative_luminance,
    auto_fg_color,
    opposite_hue_color,
    opposite_contrast_color,
    inverted_rgb,
    accent_low,
    accent_strong,
    variants_from_anchor,
    fg_variants,
    parse_color_rgb,
)

from helpers.theme_palette import generate_palette

from helpers.color.color_types import ColorRGB


def test_rgb_hsv_roundtrip_loose():
    c = ColorRGB(120, 60, 200)
    h, s, v = rgb_to_hsv(c)
    c2 = hsv_to_rgb(h, s, v)
    # allow some rounding drift
    assert abs(c2.r - c.r) <= 2
    assert abs(c2.g - c.g) <= 2
    assert abs(c2.b - c.b) <= 2


def test_blend_and_luminance_fg():
    a = ColorRGB(0, 0, 0)
    b = ColorRGB(255, 255, 255)
    mid = blend_rgb(a, b, 0.5)
    assert 120 <= mid.r <= 135
    assert 120 <= mid.g <= 135
    assert 120 <= mid.b <= 135

    assert relative_luminance(ColorRGB(255, 255, 255)) > relative_luminance(ColorRGB(0, 0, 0))
    assert auto_fg_color(ColorRGB(250, 250, 250)) == ColorRGB(0, 0, 0)
    assert auto_fg_color(ColorRGB(10, 10, 10)) == ColorRGB(255, 255, 255)


def test_opposites_and_inversion():
    c = ColorRGB(10, 20, 30)
    inv = inverted_rgb(c)
    assert inv == ColorRGB(245, 235, 225)

    opp = opposite_hue_color(ColorRGB(255, 0, 0))
    # opposite hue of red is around cyan-ish; avoid exact assertions
    assert isinstance(opp.r, int) and isinstance(opp.g, int) and isinstance(opp.b, int)

    opp2 = opposite_contrast_color(ColorRGB(10, 10, 10))
    assert isinstance(opp2.r, int)


def test_accents_and_variants():
    base = ColorRGB(50, 100, 150)
    al = accent_low(base)
    ah = accent_strong(base)
    assert isinstance(al.r, int) and isinstance(ah.r, int)

    vars_ = variants_from_anchor(base, include_extremes=True)
    assert vars_.low is not None
    assert vars_.muted is not None
    assert vars_.high is not None
    assert vars_.very_low is not None
    assert vars_.very_high is not None

    fg_m, fg_h = fg_variants(ColorRGB(250, 250, 250), toward=base)
    assert isinstance(fg_m.r, int)
    assert isinstance(fg_h.r, int)


def test_parse_color_rgb():
    assert parse_color_rgb("#ff00aa") == ColorRGB(255, 0, 170)
    assert parse_color_rgb("255, 0, 170") == ColorRGB(255, 0, 170)
    assert parse_color_rgb("rgb(255,0,170)") == ColorRGB(255, 0, 170)
    with pytest.raises(ValueError):
        parse_color_rgb("#fff")  # wrong length


def test_generate_palette_smoke():
    p = generate_palette(base=ColorRGB(30, 30, 30))
    assert p.base == ColorRGB(30, 30, 30)
    assert p.fg in (ColorRGB(255, 255, 255), ColorRGB(0, 0, 0))
    assert isinstance(p.warning.r, int)
