"""Compatibility shim for legacy app.* imports."""

from importlib import import_module as _import_module
import sys as _sys

_toolkit_adapters = _import_module("my_toolkit.toolkit_adapters")
_sys.modules[__name__] = _toolkit_adapters
