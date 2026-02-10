from __future__ import annotations

from dataclasses import dataclass

from helpers.lighting.pixel_buffer_editor import PixelBufferEditor
from helpers.lighting.pixel_strips_model import PixelColorRGB, seed_pixel_strips_doc


@dataclass
class EditableDoc:
    raw: dict


def _make_editor() -> PixelBufferEditor:
    doc = seed_pixel_strips_doc()
    return PixelBufferEditor(EditableDoc(raw=doc))


def test_resize_pixels_increase_preserves_prefix() -> None:
    editor = _make_editor()
    strip_id = editor.create_strip(strip_id="strip_resize", pixel_count=3)

    editor.set_pixel(strip_id, 0, PixelColorRGB(1, 2, 3))
    editor.set_pixel(strip_id, 1, PixelColorRGB(4, 5, 6))
    editor.set_pixel(strip_id, 2, PixelColorRGB(7, 8, 9))

    editor.resize_pixels(strip_id, 5, fill=PixelColorRGB(9, 9, 9))

    raw = editor.editable.raw["strips"][0]
    pixels = raw["pixels"]
    assert raw["pixel_count"] == 5
    assert len(pixels) == 5
    assert pixels[:3] == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert pixels[3:] == [[9, 9, 9], [9, 9, 9]]


def test_resize_pixels_decrease_preserves_prefix() -> None:
    editor = _make_editor()
    strip_id = editor.create_strip(strip_id="strip_shrink", pixel_count=4)

    editor.set_pixel(strip_id, 0, PixelColorRGB(10, 10, 10))
    editor.set_pixel(strip_id, 1, PixelColorRGB(20, 20, 20))
    editor.set_pixel(strip_id, 2, PixelColorRGB(30, 30, 30))
    editor.set_pixel(strip_id, 3, PixelColorRGB(40, 40, 40))

    editor.resize_pixels(strip_id, 2)

    raw = editor.editable.raw["strips"][0]
    pixels = raw["pixels"]
    assert raw["pixel_count"] == 2
    assert len(pixels) == 2
    assert pixels == [[10, 10, 10], [20, 20, 20]]
