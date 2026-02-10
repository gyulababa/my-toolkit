"""Compatibility shim for legacy app.adapters.* imports."""

from importlib import import_module as _import_module
import sys as _sys

_adapters = _import_module("my_toolkit.toolkit_adapters.adapters")
_sys.modules[__name__] = _adapters
