# helpers/transforms/__init__.py
"""helpers.transforms

Generic, project-agnostic transform utilities.

Structure (locked):
- helpers.transforms.imaging  : numpy-array transforms (crop/resize/colors)
- helpers.transforms.bytes    : bytes payload transforms (LED RGB frames, etc.)

Note:
- Vision-specific "Frame wrappers" live in helpers.vision.transforms
  and delegate to these pure transforms.
"""

from __future__ import annotations

from . import imaging as imaging
from . import bytes as _bytes

# Provide attribute access as `helpers.transforms.bytes`.
bytes = _bytes

del _bytes

__all__ = ["imaging", "bytes"]
