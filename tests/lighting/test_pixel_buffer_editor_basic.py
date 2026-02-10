from __future__ import annotations

from dataclasses import dataclass

from helpers.lighting.pixel_buffer_editor import PixelBufferEditor
from helpers.lighting.pixel_strips_model import (
    Endpoint,
    PixelColorRGB,
    StripType,
    seed_pixel_strips_doc,
)


@dataclass
class EditableDoc:
    raw: dict


def _make_editor() -> PixelBufferEditor:
    doc = seed_pixel_strips_doc()
    return PixelBufferEditor(EditableDoc(raw=doc))


def test_create_delete_strip() -> None:
    editor = _make_editor()

    strip_id = editor.create_strip(
        strip_id="strip_a",
        pixel_count=3,
        strip_type=StripType.WLED,
        display_name="Main",
        aliases=["main"],
        endpoint=Endpoint(kind="ddp", host="127.0.0.1", port=4048),
        placement="front",
        master_brightness=0.75,
    )
    assert strip_id == "strip_a"

    strips = editor.editable.raw["strips"]
    assert len(strips) == 1
    raw = strips[0]
    assert raw["id"] == "strip_a"
    assert raw["type"] == "wled"
    assert raw["pixel_count"] == 3
    assert len(raw["pixels"]) == 3

    editor.delete_strip("strip_a")
    assert editor.editable.raw["strips"] == []


def test_set_pixel_fill_set_range() -> None:
    editor = _make_editor()
    strip_id = editor.create_strip(strip_id="strip_b", pixel_count=5)

    editor.set_pixel(strip_id, 2, PixelColorRGB(10, 20, 30))
    pixels = editor.editable.raw["strips"][0]["pixels"]
    assert pixels[2] == [10, 20, 30]

    editor.fill(strip_id, PixelColorRGB(1, 2, 3))
    pixels = editor.editable.raw["strips"][0]["pixels"]
    assert pixels == [[1, 2, 3]] * 5

    editor.set_range(strip_id, 1, 2, PixelColorRGB(9, 9, 9))
    pixels = editor.editable.raw["strips"][0]["pixels"]
    assert pixels[0] == [1, 2, 3]
    assert pixels[1] == [9, 9, 9]
    assert pixels[2] == [9, 9, 9]
    assert pixels[3] == [1, 2, 3]
    assert pixels[4] == [1, 2, 3]


def test_render_rgb_bytes_applies_brightness() -> None:
    editor = _make_editor()
    strip_id = editor.create_strip(strip_id="strip_c", pixel_count=2)

    editor.set_pixel(strip_id, 0, PixelColorRGB(10, 20, 30))
    editor.set_pixel(strip_id, 1, PixelColorRGB(100, 110, 120))
    editor.set_master_brightness(strip_id, 0.5)

    payload = editor.render_rgb_bytes(strip_id)
    assert payload == bytes([5, 10, 15, 50, 55, 60])
