# helpers/led_pixels/model.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple


# -------------------------
# Value objects
# -------------------------

@dataclass(frozen=True, slots=True)
class PixelColorRGB:
    """Simple RGB color (0..255 each)."""
    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        for name, v in (("r", self.r), ("g", self.g), ("b", self.b)):
            if not isinstance(v, int):
                raise TypeError(f"{name} must be int, got {type(v).__name__}")
            if v < 0 or v > 255:
                raise ValueError(f"{name} must be 0..255, got {v}")

    @staticmethod
    def black() -> "PixelColorRGB":
        return PixelColorRGB(0, 0, 0)

    def with_brightness(self, scale: float) -> "PixelColorRGB":
        """Scale brightness (0..1+)."""
        if not isinstance(scale, (int, float)):
            raise TypeError("scale must be a number")
        r = max(0, min(255, int(round(self.r * scale))))
        g = max(0, min(255, int(round(self.g * scale))))
        b = max(0, min(255, int(round(self.b * scale))))
        return PixelColorRGB(r, g, b)


@dataclass(frozen=True, slots=True)
class AddressablePixel:
    """A pixel at a specific index with a color."""
    index: int
    color: PixelColorRGB

    def __post_init__(self) -> None:
        if not isinstance(self.index, int):
            raise TypeError("index must be int")
        if self.index < 0:
            raise ValueError("index must be >= 0")


# -------------------------
# Core state: ordered pixels
# -------------------------

class PixelBuffer:
    """
    Canonical ordered pixel state.

    This is the core 'strip-like' object, but named frontend-agnostically.
    Anything that transmits frames (DDP/ArtNet/sACN) consumes this buffer.
    """

    def __init__(self, size: int, default: Optional[PixelColorRGB] = None) -> None:
        if not isinstance(size, int):
            raise TypeError("size must be int")
        if size < 0:
            raise ValueError("size must be >= 0")
        default = default or PixelColorRGB.black()
        self._colors: List[PixelColorRGB] = [default] * size

    # --- basic container semantics ---
    def __len__(self) -> int:
        return len(self._colors)

    def iter_colors(self) -> Iterator[PixelColorRGB]:
        return iter(self._colors)

    def get(self, index: int) -> PixelColorRGB:
        self._validate_index(index)
        return self._colors[index]

    def set(self, index: int, color: PixelColorRGB) -> None:
        self._validate_index(index)
        self._colors[index] = color

    def set_many(self, indices: Iterable[int], color: PixelColorRGB) -> None:
        for i in indices:
            self.set(i, color)

    def fill(self, color: PixelColorRGB) -> None:
        for i in range(len(self._colors)):
            self._colors[i] = color

    def clear(self) -> None:
        self.fill(PixelColorRGB.black())

    def resize(self, new_size: int, fill: Optional[PixelColorRGB] = None) -> None:
        """Edit operation: change pixel count (preserves existing prefix)."""
        if not isinstance(new_size, int):
            raise TypeError("new_size must be int")
        if new_size < 0:
            raise ValueError("new_size must be >= 0")
        fill = fill or PixelColorRGB.black()
        cur = len(self._colors)
        if new_size == cur:
            return
        if new_size < cur:
            del self._colors[new_size:]
        else:
            self._colors.extend([fill] * (new_size - cur))

    def insert_pixels(self, at: int, count: int, fill: Optional[PixelColorRGB] = None) -> None:
        """Edit operation: insert count pixels at index (shifts later pixels right)."""
        if not isinstance(at, int) or not isinstance(count, int):
            raise TypeError("at and count must be int")
        if at < 0 or at > len(self._colors):
            raise ValueError("at out of range")
        if count < 0:
            raise ValueError("count must be >= 0")
        fill = fill or PixelColorRGB.black()
        if count == 0:
            return
        self._colors[at:at] = [fill] * count

    def delete_pixels(self, at: int, count: int) -> None:
        """Edit operation: delete count pixels starting at index (shifts later pixels left)."""
        if not isinstance(at, int) or not isinstance(count, int):
            raise TypeError("at and count must be int")
        if count < 0:
            raise ValueError("count must be >= 0")
        if at < 0 or at > len(self._colors):
            raise ValueError("at out of range")
        end = min(len(self._colors), at + count)
        del self._colors[at:end]

    # --- spans/groups helpers ---
    def span(self, start: int, length: int) -> "PixelSpan":
        return PixelSpan(self, start, length)

    def group(self, name: str, indices: Iterable[int]) -> "PixelGroup":
        return PixelGroup(self, name=name, indices=set(indices))

    # --- output / interop ---
    def to_rgb_bytes(self) -> bytes:
        """Packed RGB bytes (3 bytes per pixel), suitable for DDP."""
        out = bytearray(3 * len(self._colors))
        j = 0
        for c in self._colors:
            out[j] = c.r
            out[j + 1] = c.g
            out[j + 2] = c.b
            j += 3
        return bytes(out)

    def _validate_index(self, index: int) -> None:
        if not isinstance(index, int):
            raise TypeError("index must be int")
        if index < 0 or index >= len(self._colors):
            raise IndexError(f"index {index} out of range (0..{len(self._colors)-1})")


# -------------------------
# Contiguous segment (span)
# -------------------------

@dataclass(slots=True)
class PixelSpan:
    """
    A contiguous region within a PixelBuffer.

    Holds a *reference* to the buffer, so edits apply directly to the buffer.
    """
    buffer: PixelBuffer
    start: int
    length: int

    def __post_init__(self) -> None:
        if self.length < 0:
            raise ValueError("length must be >= 0")
        if self.start < 0:
            raise ValueError("start must be >= 0")
        if self.start + self.length > len(self.buffer):
            raise ValueError("span exceeds buffer size")

    @property
    def end_exclusive(self) -> int:
        return self.start + self.length

    def indices(self) -> range:
        return range(self.start, self.end_exclusive)

    # edit ops
    def set_all(self, color: PixelColorRGB) -> None:
        for i in self.indices():
            self.buffer.set(i, color)

    def set_at(self, offset: int, color: PixelColorRGB) -> None:
        if offset < 0 or offset >= self.length:
            raise IndexError("offset out of span range")
        self.buffer.set(self.start + offset, color)

    def shift(self, delta: int) -> None:
        """Edit operation: move the span window (does not move underlying pixels)."""
        ns = self.start + int(delta)
        if ns < 0 or ns + self.length > len(self.buffer):
            raise ValueError("shift would move span out of bounds")
        self.start = ns

    def resize(self, new_length: int) -> None:
        """Edit operation: resize the span window (does not resize buffer)."""
        nl = int(new_length)
        if nl < 0:
            raise ValueError("new_length must be >= 0")
        if self.start + nl > len(self.buffer):
            raise ValueError("resize would exceed buffer")
        self.length = nl

    def subspan(self, offset: int, length: int) -> "PixelSpan":
        """Create a child span inside this span."""
        if offset < 0 or length < 0:
            raise ValueError("offset/length must be >= 0")
        if offset + length > self.length:
            raise ValueError("subspan exceeds parent span")
        return PixelSpan(self.buffer, self.start + offset, length)


# -------------------------
# Arbitrary set of pixels
# -------------------------

@dataclass(slots=True)
class PixelGroup:
    """
    Named, non-contiguous set of indices in a buffer.
    Useful for 'zones', 'clusters', 'fixtures', etc.
    """
    buffer: PixelBuffer
    name: str
    indices_set: set[int]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must be non-empty")
        # validate indices now (fail fast)
        for i in self.indices_set:
            self.buffer.get(i)  # validates range

    def indices(self) -> List[int]:
        return sorted(self.indices_set)

    # edit ops
    def add(self, index: int) -> None:
        self.buffer.get(index)  # validate
        self.indices_set.add(index)

    def remove(self, index: int) -> None:
        self.indices_set.remove(index)

    def clear(self) -> None:
        self.indices_set.clear()

    def set_all(self, color: PixelColorRGB) -> None:
        self.buffer.set_many(self.indices_set, color)

    def rename(self, new_name: str) -> None:
        if not new_name:
            raise ValueError("new_name must be non-empty")
        self.name = new_name


# -------------------------
# Optional: layout registry
# -------------------------

class PixelLayout:
    """
    Registry of named spans/groups over a single PixelBuffer.

    This is the "explanatory" layer: it turns raw indices into meaningful fixtures.
    """
    def __init__(self, buffer: PixelBuffer) -> None:
        self.buffer = buffer
        self.spans: Dict[str, PixelSpan] = {}
        self.groups: Dict[str, PixelGroup] = {}

    # edit ops
    def define_span(self, name: str, start: int, length: int) -> PixelSpan:
        if not name:
            raise ValueError("name must be non-empty")
        span = PixelSpan(self.buffer, start, length)
        self.spans[name] = span
        return span

    def define_group(self, name: str, indices: Iterable[int]) -> PixelGroup:
        if not name:
            raise ValueError("name must be non-empty")
        grp = PixelGroup(self.buffer, name=name, indices_set=set(indices))
        self.groups[name] = grp
        return grp

    def delete_span(self, name: str) -> None:
        del self.spans[name]

    def delete_group(self, name: str) -> None:
        del self.groups[name]
