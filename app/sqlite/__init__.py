"""Compatibility shim for legacy app.sqlite.* imports."""

from importlib import import_module as _import_module
import sys as _sys

_sqlite = _import_module("my_toolkit.toolkit_adapters.sqlite")
_sys.modules[__name__] = _sqlite
