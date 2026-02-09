# app/adapters/dearpygui/vision/dpg_texture_pool.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from app.adapters.dearpygui.vision.dpg_texture import DpgTexture


@dataclass(frozen=True)
class TextureRef:
    texture_tag: str


class DpgTexturePool:
    """
    Owns one texture_registry + multiple DpgTexture objects by name.
    """

    def __init__(self, *, dpg, registry_tag: str = "texreg.main"):
        self._dpg = dpg
        self._registry_tag = registry_tag
        self._registry_ready = False
        self._textures: Dict[str, DpgTexture] = {}

    @property
    def registry_tag(self) -> str:
        return self._registry_tag

    def ensure_registry(self) -> None:
        if self._registry_ready:
            return
        self._dpg.add_texture_registry(tag=self._registry_tag, show=False)
        self._registry_ready = True

    def ensure(self, name: str, *, size: Tuple[int, int] = (2, 2)) -> TextureRef:
        self.ensure_registry()
        tex = self._textures.get(name)
        if tex is None:
            tex = DpgTexture(dpg=self._dpg, texture_tag=f"tex::{name}")
            self._textures[name] = tex
        tex.ensure_created(width=int(size[0]), height=int(size[1]), registry_tag=self._registry_tag)
        return TextureRef(texture_tag=tex.texture_tag)

    def update_rgba_u8(self, name: str, rgba_u8, *, allow_resize: bool = True) -> TextureRef:
        self.ensure_registry()
        tex = self._textures.get(name)
        if tex is None:
            tex = DpgTexture(dpg=self._dpg, texture_tag=f"tex::{name}")
            self._textures[name] = tex
        tex.update_rgba_u8(rgba_u8, allow_resize=allow_resize, registry_tag=self._registry_tag)
        return TextureRef(texture_tag=tex.texture_tag)

    def get(self, name: str) -> Optional[TextureRef]:
        t = self._textures.get(name)
        if t is None:
            return None
        return TextureRef(texture_tag=t.texture_tag)
