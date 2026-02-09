# helpers/vision/clock.py
# Vision-specific timing wrapper (delegates to helpers.threading.RateLimiter).

from __future__ import annotations

"""
helpers.vision.clock
--------------------

This module exists for backward compatibility and to keep the vision package
self-contained, but the canonical implementation now lives in helpers.threading.

Prefer importing:
  from helpers.threading import RateLimiter
"""

from helpers.threading import RateLimiter

__all__ = ["RateLimiter"]
