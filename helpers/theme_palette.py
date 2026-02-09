# helpers/theme_palette.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from helpers.color.color_types import ColorRGB

from helpers.math.basic import clamp01
from helpers.color.color_utils import (
    auto_fg_color,
    opposite_hue_color,
    variants_from_anchor,
    fg_variants,
    blend_rgb,
    rgb_to_hsv,
    hsv_to_rgb,
)

# Warning color policy:
# - "global": fixed amber/orange regardless of base
# - "relative": derive warning from base (warm hue) while keeping high visibility
WarningMode = Literal["global", "relative"]


@dataclass(frozen=True)
class ThemePalette:
    """
    A small, UI-agnostic color palette meant to be shared across frontends.

    Terminology:
    - Anchors: the primary "source" colors (base/accent/fg).
    - Variants: derived colors (_low/_muted/_high) used for surfaces/emphasis.
    - Semantics: special-purpose colors that keep meaning across the app (warning).

    Notes:
    - `fg` is intentionally named neutrally (not "text") so this can be reused in
      non-UI contexts (e.g. debug overlays, console previews, etc.).
    """

    # ── Anchors (resolved) ─────────────────────────────────────
    base: ColorRGB
    accent: ColorRGB
    fg: ColorRGB

    # ── Base variants ─────────────────────────────────────────
    base_low: ColorRGB
    base_muted: ColorRGB
    base_high: ColorRGB

    # ── Accent variants ───────────────────────────────────────
    accent_low: ColorRGB
    accent_muted: ColorRGB
    accent_high: ColorRGB

    # ── Foreground variants ───────────────────────────────────
    fg_muted: ColorRGB
    fg_high: ColorRGB

    # ── Semantics ─────────────────────────────────────────────
    warning: ColorRGB


def generate_palette(
    *,
    base: ColorRGB,
    accent: Optional[ColorRGB] = None,
    fg: Optional[ColorRGB] = None,
    warning_mode: WarningMode = "global",
    cohesion: float = 0.15,
) -> ThemePalette:
    """
    Generate a theme palette from 1–3 user-provided colors.

    Inputs:
    - base (required): primary surface/background anchor.
    - accent (optional): secondary/interactive anchor. If missing, uses an
      opposite-hue color derived from base.
    - fg (optional): foreground/content anchor. If missing, chooses an automatic
      high-contrast fg (black/white style) from base.

    Cohesion:
    - cohesion ∈ [0..1] softly pulls accent variants toward base to keep the palette
      feeling "one family" (useful when accent is highly saturated or off-theme).
      cohesion=0.0 -> do not mix
      cohesion=1.0 -> stronger mixing

    Warning:
    - global: fixed amber/orange (stable semantic)
    - relative: warm warning derived from base hue space, then lightly blended with base
    """
    cohesion = clamp01(cohesion)

    # ── Resolve anchors ────────────────────────────────────────
    base_c = base
    accent_c = accent if accent is not None else opposite_hue_color(base_c)
    fg_c = fg if fg is not None else auto_fg_color(base_c)

    # ── Derive base variants ───────────────────────────────────
    # These are tuned to give:
    # - low: a gentle tint toward "off" state for fills/backgrounds
    # - muted: reduced saturation/value for secondary surfaces
    # - high: higher emphasis surface/edge
    base_vars = variants_from_anchor(
        base_c,
        low_alpha=0.30,
        muted_sat=0.20,
        muted_val=0.45,
        high_sat=0.75,
        high_val=0.85,
        include_extremes=False,
    )

    # ── Derive accent variants ─────────────────────────────────
    # Accent variants optionally cohere toward base so accents feel integrated.
    accent_vars = variants_from_anchor(
        accent_c,
        low_alpha=0.25,
        muted_sat=0.22,
        muted_val=0.45,
        high_sat=0.85,
        high_val=0.90,
        cohesion_with=base_c,
        cohesion_alpha=cohesion,
        include_extremes=False,
    )

    # ── Derive foreground variants ─────────────────────────────
    # `fg_variants` returns two useful emphasis levels:
    # - fg_muted: closer to base, used for secondary labels/values
    # - fg_high: stronger contrast / "headline" emphasis
    fg_muted, fg_high = fg_variants(
        fg_c,
        muted_alpha=0.60,
        high_alpha=0.30,
        toward=base_c,
    )

    # ── Semantics: warning ─────────────────────────────────────
    if warning_mode == "global":
        warning = ColorRGB(255, 140, 0)  # amber/orange
    else:
        # Relative warm warning:
        # - Use a warm hue (~orange)
        # - Keep saturation/value high for visibility
        # - Optionally blend slightly toward base for cohesion
        h, s, v = rgb_to_hsv(base_c)
        warning_raw = hsv_to_rgb(0.08, max(s, 0.85), max(v, 0.90))  # ~orange
        warning = blend_rgb(warning_raw, base_c, cohesion * 0.25)

    return ThemePalette(
        # anchors
        base=base_c,
        accent=accent_c,
        fg=fg_c,

        # base variants
        base_low=base_vars.low,
        base_muted=base_vars.muted,
        base_high=base_vars.high,

        # accent variants
        accent_low=accent_vars.low,
        accent_muted=accent_vars.muted,
        accent_high=accent_vars.high,

        # foreground variants
        fg_muted=fg_muted,
        fg_high=fg_high,

        # semantics
        warning=warning,
    )
