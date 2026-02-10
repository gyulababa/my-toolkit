"""Compatibility shim for helpers.* imports under my_toolkit.helpers.*."""

from importlib import import_module as _import_module
import sys as _sys

_helpers = _import_module("helpers")
_sys.modules[__name__] = _helpers
