"""Compatibility shim for services.* imports under my_toolkit.services.*."""

from importlib import import_module as _import_module
import sys as _sys

_services = _import_module("services")
_sys.modules[__name__] = _services
