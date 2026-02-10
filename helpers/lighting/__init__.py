"""Compatibility shim for helpers.lighting.* imports (moved to helpers.led_pixels)."""

from importlib import import_module as _import_module
import sys as _sys

_led_pixels = _import_module("helpers.led_pixels")
_sys.modules[__name__] = _led_pixels
