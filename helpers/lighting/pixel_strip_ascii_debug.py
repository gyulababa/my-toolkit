from __future__ import annotations

from typing import List, Tuple

from helpers.strip_map import FixedStrip
from helpers.strip_preview_ascii import preview_ranges_with_labels

from .pixel_buffer_editor import PixelBufferEditor


def preview_whole_strip_ascii(editor: PixelBufferEditor, strip_id: str) -> str:
    """
    Debug: render one character per pixel showing whether it's black or not.
    Not a color preview -- just a quick "activity" map.
    """
    doc = editor.editable.raw
    idx = editor._find_strip_index(strip_id)  # internal helper, OK for debug
    s = doc["strips"][idx]
    pixels = s.get("pixels", [])
    strip = FixedStrip(length=len(pixels))

    # Build ranges of "non-black" runs for quick inspection
    ranges: List[Tuple[int, int]] = []
    cur_start = None
    for i, t in enumerate(pixels):
        is_on = (int(t[0]) or int(t[1]) or int(t[2])) != 0
        if is_on and cur_start is None:
            cur_start = i
        if (not is_on) and cur_start is not None:
            ranges.append((cur_start, i))
            cur_start = None
    if cur_start is not None:
        ranges.append((cur_start, len(pixels)))

    names = [f"on_{k}" for k in range(len(ranges))]
    return preview_ranges_with_labels(strip, ranges, names)

