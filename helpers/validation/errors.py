# helpers/validation/errors.py
# Shared error types and small formatting helpers for validation (canonical ValidationError + message utilities).

from __future__ import annotations

from typing import Any


class ValidationError(ValueError):
    """
    Raised when validation fails.

    We intentionally subclass ValueError because:
    - it is idiomatic for "bad value" situations
    - callers often already handle ValueError broadly
    - config/schema errors should generally not be treated as programmer errors
    """
    pass


def type_name(x: Any) -> str:
    """Return a stable type name for error messages."""
    return type(x).__name__


def qpath(path: str) -> str:
    """
    Quote a dotted path for consistent error messages.

    Examples:
      qpath("a.b") -> "'a.b'"
      qpath("")    -> "'value'"
    """
    p = path if path else "value"
    return f"'{p}'"
