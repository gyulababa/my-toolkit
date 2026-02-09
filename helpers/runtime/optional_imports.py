# helpers/runtime/optional_imports.py
# Generic optional-import helper: import a module lazily and raise a friendly error with install hints.

from __future__ import annotations

"""
helpers.runtime.optional_imports
--------------------------------

Generic helper to import optional dependencies at runtime.

Why this exists:
- Many toolkit components are optional-dependency friendly (e.g., mss, cv2, dearpygui).
- We want consistent, helpful error messages without duplicating `_require_xxx()` helpers.

Non-goals:
- Dependency management / pinning
- Environment inspection beyond a simple import attempt
"""

from importlib import import_module
from types import ModuleType
from typing import Optional


def require(module_path: str, *, pip_hint: Optional[str] = None, purpose: Optional[str] = None) -> ModuleType:
    """
    Import a module by dotted path (e.g. "cv2" or "dearpygui.dearpygui").

    Args:
      module_path: Dotted import path to import.
      pip_hint: Optional pip package name to suggest (e.g. "opencv-python", "dearpygui").
      purpose: Optional short note about what feature needs the dependency.

    Returns:
      The imported module object.

    Raises:
      RuntimeError: if the module cannot be imported, with a friendly message.
    """
    try:
        return import_module(module_path)
    except Exception as e:
        msg = f"Missing optional dependency '{module_path}'."
        if purpose:
            msg += f" Required for: {purpose}."
        if pip_hint:
            msg += f" Install via: pip install {pip_hint}"
        raise RuntimeError(msg) from e
