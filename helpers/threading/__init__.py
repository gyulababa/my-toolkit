# helpers/threading/__init__.py
# Public exports for helpers.threading (small concurrency/timing primitives).

"""
helpers.threading

Small, reusable threading/runtime helpers.

Scope:
- rate limiting / tick pacing for background loops

Non-goals:
- thread pools, async runtimes, complex scheduling abstractions
"""

from .rate_limiter import RateLimiter

__all__ = ["RateLimiter"]
