# app/adapters/dearpygui/vision/dpg_texture.py
# UPDATED: supports creating textures under a provided texture_registry tag.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class DpgTexture:
    dpg: object
    texture_tag: str
    image_tag: Optional[str] = None

    width: int = 2
    height: int = 2

    _created: bool = False
    _fmt_kind: str = "u8"  # "u8" or "float"

    def bind_image(self, image_tag: str) -> None:
        self.image_tag = image_tag
        if self._created and self.dpg.does_item_exist(self.texture_tag) and self.dpg.does_item_exist(image_tag):
            self.dpg.configure_item(image_tag, texture_tag=self.texture_tag)

    def _resolve_rgba_format(self) -> int:
        fmt = getattr(self.dpg, "mvFormat_U8_rgba8", None)
        if fmt is not None:
            self._fmt_kind = "u8"
            return fmt

        fmt = getattr(self.dpg, "mvFormat_Float_rgba", None)
        if fmt is not None:
            self._fmt_kind = "float"
            return fmt

        raise AttributeError(
            "DearPyGui: no compatible RGBA raw texture format found. "
            "Expected mvFormat_U8_rgba8 or mvFormat_Float_rgba."
        )

    def _bind_image_if_ready(self) -> None:
        if not self.image_tag:
            return
        if not self.dpg.does_item_exist(self.image_tag):
            return
        if not self.dpg.does_item_exist(self.texture_tag):
            return
        self.dpg.configure_item(self.image_tag, texture_tag=self.texture_tag)

    def ensure_created(self, *, width: int, height: int, registry_tag: Optional[str] = None) -> None:
        width = int(width)
        height = int(height)
        if width <= 0 or height <= 0:
            raise ValueError(f"DpgTexture.ensure_created: invalid size {width}x{height}")

        if self._created and self.dpg.does_item_exist(self.texture_tag):
            return

        self.width = width
        self.height = height

        zeros_u8 = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        fmt = self._resolve_rgba_format()

        if self._fmt_kind == "u8":
            default_value = zeros_u8.flatten()
        else:
            default_value = (zeros_u8.astype(np.float32) / 255.0).flatten()

        if registry_tag is not None:
            self.dpg.push_container_stack(registry_tag)
            try:
                self.dpg.add_raw_texture(
                    width=self.width,
                    height=self.height,
                    default_value=default_value,
                    format=fmt,
                    tag=self.texture_tag,
                )
            finally:
                self.dpg.pop_container_stack()
        else:
            with self.dpg.texture_registry(show=False):
                self.dpg.add_raw_texture(
                    width=self.width,
                    height=self.height,
                    default_value=default_value,
                    format=fmt,
                    tag=self.texture_tag,
                )

        self._created = True
        self._bind_image_if_ready()

    def _retag_for_resize(self) -> None:
        suffix = 1
        base = self.texture_tag.split("#", 1)[0]
        new_tag = f"{base}#{suffix}"
        while self.dpg.does_item_exist(new_tag):
            suffix += 1
            new_tag = f"{base}#{suffix}"
        self.texture_tag = new_tag
        self._created = False

    def update_rgba_u8(self, rgba_u8: np.ndarray, *, allow_resize: bool = True, registry_tag: Optional[str] = None) -> None:
        if rgba_u8.ndim != 3 or rgba_u8.shape[2] != 4:
            raise ValueError(f"DpgTexture.update_rgba_u8: expected HxWx4, got {rgba_u8.shape!r}")

        h, w, _ = rgba_u8.shape

        if (w != self.width or h != self.height) and allow_resize:
            self.width, self.height = int(w), int(h)
            self._retag_for_resize()

        self.ensure_created(width=self.width, height=self.height, registry_tag=registry_tag)

        if self._fmt_kind == "u8":
            data = rgba_u8.flatten()
        else:
            data = (rgba_u8.astype(np.float32) / 255.0).flatten()

        self.dpg.set_value(self.texture_tag, data)
        self._bind_image_if_ready()
