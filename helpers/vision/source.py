# helpers/vision/source.py
# FrameSource protocol and best-effort metadata container for capture drivers (UI-agnostic).

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from .frame import Frame


@dataclass(frozen=True)
class SourceInfo:
    """
    Best-effort metadata describing a source.

    Drivers should populate what they can. This is used for:
      - debugging / logging
      - UI display (resolution/FPS)
      - pipeline decisions (e.g., negotiated format)
    """
    name: str
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class FrameSource(Protocol):
    """
    Contract for any frame source (screen, camera, file, etc.).

    Guidance for driver authors:
      - open()/close() should be idempotent where practical
      - read() should avoid long blocking; prefer bounded waits or internal buffering
    """

    def open(self) -> None: ...
    def close(self) -> None: ...

    def read(self) -> Optional[Frame]:
        """
        Return next frame, or None if no frame is available (non-fatal).

        The runner will call read() in a loop; returning None is a valid way to indicate:
          - "no new frame yet"
          - "temporarily unavailable"
        """
        ...

    def info(self) -> SourceInfo: ...
