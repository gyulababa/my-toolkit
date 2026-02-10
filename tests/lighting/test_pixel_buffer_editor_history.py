# tests/lighting/test_pixel_buffer_editor_history.py
from __future__ import annotations

from dataclasses import dataclass

from helpers.history.applier_tree import TreeApplier
from helpers.history.history import History
from helpers.lighting.pixel_buffer_editor import PixelBufferEditor
from helpers.lighting.pixel_strips_model import PixelColorRGB, seed_pixel_strips_doc


@dataclass
class EditableDoc:
    raw: dict


def _make_editor_with_history() -> tuple[PixelBufferEditor, History]:
    doc = seed_pixel_strips_doc()
    history = History(applier=TreeApplier(), doc=doc)
    editor = PixelBufferEditor(EditableDoc(raw=doc), history=history)
    return editor, history


def test_history_bound_pushes_ops_and_undo_redo() -> None:
    editor, history = _make_editor_with_history()

    strip_id = editor.create_strip(strip_id="hist_strip", pixel_count=2)
    assert len(history.undo_stack) == 1

    editor.set_pixel(strip_id, 0, PixelColorRGB(9, 8, 7))
    assert len(history.undo_stack) == 2
    assert history.doc["strips"][0]["pixels"][0] == [9, 8, 7]

    history.undo(history.doc)
    assert history.doc["strips"][0]["pixels"][0] == [0, 0, 0]

    history.redo(history.doc)
    assert history.doc["strips"][0]["pixels"][0] == [9, 8, 7]

    editor.delete_strip(strip_id)
    assert history.doc["strips"] == []

    history.undo(history.doc)
    assert history.doc["strips"][0]["id"] == strip_id
