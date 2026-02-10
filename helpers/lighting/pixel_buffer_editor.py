from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple
from uuid import uuid4

from .pixel_strips_model import (
    Endpoint,
    PixelColorRGB,
    StripType,
    apply_master_brightness_to_rgb_triplet,
    normalize_master_brightness,
    seed_strip_raw,
)


# -------------------------
# Minimal duck-typing interface for your EditableCatalog
# -------------------------

class HasRaw(Protocol):
    raw: Dict[str, Any]


@dataclass
class PixelBufferEditor:
    """
    Frontend-agnostic editor for pixel strips stored in a raw catalog doc.

    - Uses History.push_* helpers when history is provided+bound (history.doc is set). 
    - Falls back to direct mutation if history is None.
    """
    editable: HasRaw
    history: Optional[Any] = None  # helpers.history.history.History

    # ---------- utilities ----------
    def _doc(self) -> Dict[str, Any]:
        return self.editable.raw

    def _strips(self) -> List[Dict[str, Any]]:
        doc = self._doc()
        strips = doc.get("strips", None)
        if not isinstance(strips, list):
            raise TypeError("doc['strips'] must be a list")
        return strips

    def _find_strip_index(self, strip_id: str) -> int:
        for i, s in enumerate(self._strips()):
            if isinstance(s, dict) and s.get("id") == strip_id:
                return i
        raise KeyError(f"strip_id not found: {strip_id}")

    def _ensure_history_bound(self) -> bool:
        return self.history is not None and getattr(self.history, "doc", None) is self._doc()

    def _begin_batch(self, label: str) -> None:
        if self.history is not None:
            self.history.begin_batch(label)

    def _end_batch(self) -> None:
        if self.history is not None:
            self.history.end_batch()

    # ---------- strip lifecycle ----------
    def create_strip(
        self,
        *,
        pixel_count: int,
        strip_type: StripType = StripType.OTHER,
        display_name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        endpoint: Optional[Endpoint] = None,
        placement: Optional[str] = None,
        master_brightness: float = 1.0,
        fill: Optional[PixelColorRGB] = None,
        strip_id: Optional[str] = None,
    ) -> str:
        """
        Create a new strip. ID is required logically; generated if not provided.
        """
        sid = strip_id or uuid4().hex
        raw = seed_strip_raw(
            strip_id=sid,
            pixel_count=pixel_count,
            strip_type=strip_type,
            display_name=display_name,
            aliases=aliases,
            endpoint=endpoint,
            placement=placement,
            master_brightness=master_brightness,
            fill=fill,
        )

        if self._ensure_history_bound():
            self.history.push_list_append(["strips"], raw)
        else:
            self._strips().append(raw)
        return sid

    def delete_strip(self, strip_id: str) -> None:
        idx = self._find_strip_index(strip_id)
        if self._ensure_history_bound():
            self.history.push_list_remove(["strips"], idx)
        else:
            del self._strips()[idx]

    # ---------- metadata edits ----------
    def set_display_name(self, strip_id: str, name: str) -> None:
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        names = s.setdefault("names", {"display": "", "aliases": []})
        old = str(names.get("display", ""))
        new = str(name)

        if self._ensure_history_bound():
            self.history.push_set(["strips", idx, "names", "display"], old, new)
        else:
            names["display"] = new

    def set_aliases(self, strip_id: str, aliases: List[str]) -> None:
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        names = s.setdefault("names", {"display": "", "aliases": []})
        old = list(names.get("aliases", []))
        new = list(aliases)

        if self._ensure_history_bound():
            self.history.push_set(["strips", idx, "names", "aliases"], old, new)
        else:
            names["aliases"] = new

    def set_strip_type(self, strip_id: str, strip_type: StripType) -> None:
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        old = str(s.get("type", "other"))
        new = strip_type.value
        if self._ensure_history_bound():
            self.history.push_set(["strips", idx, "type"], old, new)
        else:
            s["type"] = new

    def set_endpoint(self, strip_id: str, endpoint: Optional[Endpoint]) -> None:
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        old = s.get("endpoint", None)
        new = endpoint.to_raw() if endpoint is not None else None

        # If key existence changes, we do a conservative full set via merge/set semantics:
        # simplest: ensure endpoint key exists with None when clearing.
        if self._ensure_history_bound():
            # normalize: if old missing, treat as None, but set the key explicitly
            if "endpoint" not in s:
                s["endpoint"] = None
                old = None
            self.history.push_set(["strips", idx, "endpoint"], old, new)
        else:
            if new is None:
                s.pop("endpoint", None)
            else:
                s["endpoint"] = new

    def set_placement(self, strip_id: str, placement: Optional[str]) -> None:
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        old = s.get("placement", None)
        new = placement

        if self._ensure_history_bound():
            if "placement" not in s:
                s["placement"] = None
                old = None
            self.history.push_set(["strips", idx, "placement"], old, new)
        else:
            if new is None:
                s.pop("placement", None)
            else:
                s["placement"] = new

    def set_master_brightness(self, strip_id: str, brightness: float) -> None:
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        old = float(s.get("master_brightness", 1.0))
        new = normalize_master_brightness(brightness)

        if self._ensure_history_bound():
            self.history.push_set(["strips", idx, "master_brightness"], old, new)
        else:
            s["master_brightness"] = new

    # ---------- pixel buffer edits ----------
    def _get_pixels(self, strip_id: str) -> Tuple[int, Dict[str, Any], List[List[int]]]:
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        pixels = s.get("pixels", None)
        if not isinstance(pixels, list):
            raise TypeError("strip['pixels'] must be a list")
        return idx, s, pixels  # pixels: list[[r,g,b], ...]

    def resize_pixels(self, strip_id: str, new_count: int, *, fill: Optional[PixelColorRGB] = None) -> None:
        """
        Increase/decrease pixel_count and pixels list length.
        """
        if new_count < 0:
            raise ValueError("new_count must be >= 0")
        fill = fill or PixelColorRGB.black()

        idx, s, pixels = self._get_pixels(strip_id)
        old_count = int(s.get("pixel_count", len(pixels)))

        self._begin_batch(f"resize_pixels {strip_id} {old_count}->{new_count}")
        try:
            # update pixel_count first
            if self._ensure_history_bound():
                self.history.push_set(["strips", idx, "pixel_count"], old_count, int(new_count))
            else:
                s["pixel_count"] = int(new_count)

            if new_count > len(pixels):
                add_n = new_count - len(pixels)
                trip = fill.to_triplet()
                if self._ensure_history_bound():
                    # append via insert at end repeatedly (keeps ops invertible and simple)
                    for _ in range(add_n):
                        # push_list_append operates on list path
                        self.history.push_list_append(["strips", idx, "pixels"], list(trip))
                else:
                    pixels.extend([list(trip) for _ in range(add_n)])
            elif new_count < len(pixels):
                rem_n = len(pixels) - new_count
                if self._ensure_history_bound():
                    # remove from end repeatedly
                    for _ in range(rem_n):
                        self.history.push_list_remove(["strips", idx, "pixels"], len(pixels) - 1)
                        # pixels reference is stale after history mutation; refresh
                        pixels = self._strips()[idx]["pixels"]
                else:
                    del pixels[new_count:]
        finally:
            self._end_batch()

    def set_pixel(self, strip_id: str, index: int, color: PixelColorRGB) -> None:
        idx, s, pixels = self._get_pixels(strip_id)
        if index < 0 or index >= len(pixels):
            raise IndexError(index)

        old = pixels[index]
        new = color.to_triplet()

        if self._ensure_history_bound():
            self.history.push_set(["strips", idx, "pixels", index], old, new)
        else:
            pixels[index] = new

    def fill(self, strip_id: str, color: PixelColorRGB) -> None:
        idx, s, pixels = self._get_pixels(strip_id)
        self._begin_batch(f"fill {strip_id}")
        try:
            for i in range(len(pixels)):
                old = pixels[i]
                new = color.to_triplet()
                if self._ensure_history_bound():
                    self.history.push_set(["strips", idx, "pixels", i], old, new)
                    pixels = self._strips()[idx]["pixels"]  # refresh after history op
                else:
                    pixels[i] = new
        finally:
            self._end_batch()

    def set_range(self, strip_id: str, start: int, length: int, color: PixelColorRGB) -> None:
        if length < 0:
            raise ValueError("length must be >= 0")
        idx, s, pixels = self._get_pixels(strip_id)

        end = min(len(pixels), start + length)
        if start < 0 or start > len(pixels):
            raise IndexError("start out of range")

        self._begin_batch(f"set_range {strip_id} [{start},{end})")
        try:
            trip = color.to_triplet()
            for i in range(start, end):
                old = pixels[i]
                if self._ensure_history_bound():
                    self.history.push_set(["strips", idx, "pixels", i], old, list(trip))
                    pixels = self._strips()[idx]["pixels"]
                else:
                    pixels[i] = list(trip)
        finally:
            self._end_batch()

    # ---------- rendering (brightness applied here only) ----------
    def render_rgb_bytes(self, strip_id: str) -> bytes:
        """
        Packed RGB bytes with master brightness applied at render time.
        Safe for DDP-style senders. :contentReference[oaicite:4]{index=4}
        """
        idx = self._find_strip_index(strip_id)
        s = self._strips()[idx]
        pixels = s.get("pixels", [])
        if not isinstance(pixels, list):
            raise TypeError("strip['pixels'] must be a list")
        b = float(s.get("master_brightness", 1.0))
        out = bytearray(3 * len(pixels))
        j = 0
        for t in pixels:
            r, g, bb = apply_master_brightness_to_rgb_triplet(t, b)
            out[j] = r
            out[j + 1] = g
            out[j + 2] = bb
            j += 3
        return bytes(out)

    # ---------- lookup helpers ----------
    def list_strip_ids(self) -> List[str]:
        out: List[str] = []
        for s in self._strips():
            if isinstance(s, dict) and isinstance(s.get("id", None), str):
                out.append(s["id"])
        return out

    def find_strip_id_by_name(self, name: str) -> Optional[str]:
        """
        Case-insensitive match against display name and aliases.
        """
        q = (name or "").strip().lower()
        if not q:
            return None
        for s in self._strips():
            if not isinstance(s, dict):
                continue
            sid = s.get("id", None)
            names = s.get("names", {}) if isinstance(s.get("names", {}), dict) else {}
            disp = str(names.get("display", "")).strip().lower()
            if disp and disp == q:
                return sid
            aliases = names.get("aliases", [])
            if isinstance(aliases, list):
                for a in aliases:
                    if str(a).strip().lower() == q:
                        return sid
        return None
