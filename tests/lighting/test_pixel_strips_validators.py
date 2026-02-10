# tests/lighting/test_pixel_strips_validators.py
from __future__ import annotations

import pytest

from my_toolkit.helpers.led_pixels.pixel_strips_model import seed_pixel_strips_doc, seed_strip_raw
from my_toolkit.helpers.led_pixels.pixel_strips_validators import validate_pixel_strips_doc
from helpers.validation import ValidationError


def _make_doc() -> dict:
    doc = seed_pixel_strips_doc()
    doc["strips"].append(
        seed_strip_raw(strip_id="strip_1", pixel_count=2)
    )
    return doc


def test_validate_pixel_strips_doc_ok() -> None:
    doc = _make_doc()
    validate_pixel_strips_doc(doc)


def test_invalid_rgb_triplet_length() -> None:
    doc = _make_doc()
    doc["strips"][0]["pixels"][0] = [1, 2]
    with pytest.raises(ValidationError):
        validate_pixel_strips_doc(doc)


def test_invalid_rgb_triplet_bounds() -> None:
    doc = _make_doc()
    doc["strips"][0]["pixels"][0] = [1, 2, 300]
    with pytest.raises(ValidationError):
        validate_pixel_strips_doc(doc)


def test_invalid_master_brightness_bounds() -> None:
    doc = _make_doc()
    doc["strips"][0]["master_brightness"] = 1.5
    with pytest.raises(ValidationError):
        validate_pixel_strips_doc(doc)


def test_invalid_endpoint_missing_kind() -> None:
    doc = _make_doc()
    doc["strips"][0]["endpoint"] = {"host": "127.0.0.1"}
    with pytest.raises(ValidationError):
        validate_pixel_strips_doc(doc)


def test_duplicate_strip_ids() -> None:
    doc = seed_pixel_strips_doc()
    doc["strips"].append(seed_strip_raw(strip_id="dup", pixel_count=1))
    doc["strips"].append(seed_strip_raw(strip_id="dup", pixel_count=1))
    with pytest.raises(ValidationError):
        validate_pixel_strips_doc(doc)
