# helpers/strip_preview_ascii.py
from __future__ import annotations

from typing import Sequence, Tuple

from .strip_map import FixedStrip


def preview_ranges_ascii(
    strip: FixedStrip,
    ranges: Sequence[Tuple[int, int]],
    *,
    charset: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    empty: str = ".",
) -> str:
    """
    Render ranges into a single ASCII line of length strip.length.

    Each range is visualized using a distinct character from `charset`
    by index. If there are more ranges than available characters, the
    characters repeat (modulo charset length).

    This helper is intentionally UI-free and is designed for:
    - CLI output
    - log/debug snapshots
    - tests (visualizing range partition logic)

    Parameters:
      strip:
        FixedStrip instance that defines output length.
      ranges:
        Sequence of (start, end) half-open ranges [start, end).
      charset:
        Characters used to label ranges by index.
      empty:
        Fill character for unassigned positions (gaps).

    Returns:
      A single string with length == strip.length (or "" if length <= 0).
    """
    if strip.length <= 0:
        return ""

    line = [empty] * strip.length
    if not ranges:
        return "".join(line)

    for idx, (s, e) in enumerate(ranges):
        if e <= s:
            continue

        ch = charset[idx % len(charset)] if charset else "#"

        # clip to strip bounds
        s2 = max(0, min(strip.length, int(s)))
        e2 = max(0, min(strip.length, int(e)))

        for i in range(s2, e2):
            line[i] = ch

    return "".join(line)


def preview_playhead_ascii(
    strip: FixedStrip,
    base_line: str,
    playhead_index: int,
    *,
    marker: str = "|",
) -> str:
    """
    Overlay a playhead marker on an existing ASCII line.

    Use cases:
      - overlay a current-time playhead on top of segment ranges
      - show a moving cursor index for LED strip demos

    Requirements:
      - base_line length must equal strip.length

    Returns:
      A new string with a single character replaced by `marker`.
    """
    if strip.length <= 0:
        return ""
    if len(base_line) != strip.length:
        raise ValueError("base_line length must equal strip.length")

    i = strip.clamp_index(playhead_index)
    chars = list(base_line)
    chars[i] = marker
    return "".join(chars)


def preview_ranges_with_labels(
    strip: FixedStrip,
    ranges: Sequence[Tuple[int, int]],
    names: Sequence[str],
    *,
    charset: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    empty: str = ".",
) -> str:
    """
    Multi-line preview:

      <strip line>
      <legend line 1>
      <legend line 2>
      ...

    Where legend lines map each character to:
      "<ch>: <name> [start,end)"

    This is helpful when ranges correspond to named segments.
    """
    line = preview_ranges_ascii(strip, ranges, charset=charset, empty=empty)

    legend_lines: list[str] = []
    for idx, (s, e) in enumerate(ranges):
        ch = charset[idx % len(charset)] if charset else "#"
        name = names[idx] if idx < len(names) else f"seg_{idx}"
        legend_lines.append(f"{ch}: {name} [{int(s)},{int(e)})")

    return "\n".join([line] + legend_lines)


def preview_three_bands_ascii(length: int) -> str:
    """
    Convenience preview for a 3-band partition across a fixed-length strip.

    Purely spatial (does not represent colors).
    """
    strip = FixedStrip(length=length)
    a = length // 3
    b = (2 * length) // 3
    ranges = [(0, a), (a, b), (b, length)]
    return preview_ranges_ascii(strip, ranges)
