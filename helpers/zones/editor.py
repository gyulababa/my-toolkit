# helpers/zones/editor.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from helpers.history.ops import Operation, OpMeta
from helpers.history.history import History
from helpers.history.applier_tree import TreeApplier

import helpers.geometry.rect as geometry_rect


from .schema import ensure_library_shape


def _zone_path(preset_id: str, zone_key: str, *tail: Any) -> list[Any]:
    return ["presets", preset_id, "zones", zone_key, *tail]


@dataclass
class ZonesEditor:
    """
    Frontend-agnostic editor for the zones preset library document.

    - Works on dict/list JSON-like docs
    - Uses universal History for undo/redo
    - Performs light normalization for geometry updates

    Persistence is intentionally not included here.
    """
    doc: Dict[str, Any]
    history: History

    @classmethod
    def from_doc(cls, doc: Dict[str, Any]) -> "ZonesEditor":
        ensure_library_shape(doc)
        hist = History(applier=TreeApplier())
        return cls(doc=doc, history=hist)

    # -----------------
    # Batch helpers
    # -----------------
    def begin_batch(self, label: str = "") -> None:
        self.history.begin_batch(label)

    def end_batch(self) -> None:
        self.history.end_batch()

    def undo(self) -> None:
        self.doc = self.history.undo(self.doc)

    def redo(self) -> None:
        self.doc = self.history.redo(self.doc)

    # -----------------
    # Preset helpers
    # -----------------
    def ensure_preset(self, preset_id: str, *, name: Optional[str] = None) -> None:
        presets = self.doc.setdefault("presets", {})
        if preset_id in presets:
            return
        presets[preset_id] = {"meta": {}, "zones": {}}
        if name:
            presets[preset_id]["meta"]["name"] = name

    # -----------------
    # Zone lifecycle
    # -----------------
    def add_zone(
        self,
        preset_id: str,
        zone_key: str,
        *,
        enabled: bool = True,
        intent: str = "Custom",
        geometry: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ) -> None:
        self.ensure_preset(preset_id)
        zones = self.doc["presets"][preset_id]["zones"]
        if zone_key in zones:
            raise KeyError(f"Zone already exists: {preset_id}/{zone_key}")

        zone_obj: Dict[str, Any] = {
            "enabled": enabled,
            "intent": intent,
            "geometry": geometry or {"type": "rect_px", "xyxy": [0, 0, 1, 1]},
            "tags": tags or [],
            "style": {},
            "consumers": {},
        }

        # insert as a SET at the dict key
        path = ["presets", preset_id, "zones", zone_key]
        op = Operation(
            patch_type="set",
            path=path,
            before=None,
            after=zone_obj,
            meta=OpMeta(source="ui", reason="add_zone"),
        )
        self.doc = self.history.apply(self.doc, op)

    def remove_zone(self, preset_id: str, zone_key: str) -> None:
        zones = self.doc["presets"][preset_id]["zones"]
        if zone_key not in zones:
            return
        before = zones[zone_key]
        path = ["presets", preset_id, "zones", zone_key]
        op = Operation(
            patch_type="set",
            path=path,
            before=before,
            after=None,
            meta=OpMeta(source="ui", reason="remove_zone"),
        )
        self.doc = self.history.apply(self.doc, op)
        # Cleanup: remove key (we do a second merge op to delete is not supported by base applier)
        # For now, do direct mutation without history; later we can add "del" patch_type.
        del self.doc["presets"][preset_id]["zones"][zone_key]

    # -----------------
    # Common edits
    # -----------------
    def set_enabled(self, preset_id: str, zone_key: str, enabled: bool) -> None:
        path = _zone_path(preset_id, zone_key, "enabled")
        before = self.doc["presets"][preset_id]["zones"][zone_key].get("enabled", True)
        op = Operation(
            patch_type="set",
            path=path,
            before=before,
            after=bool(enabled),
            meta=OpMeta(source="ui", reason="set_enabled"),
        )
        self.doc = self.history.apply(self.doc, op)

    def set_intent(self, preset_id: str, zone_key: str, intent: str) -> None:
        path = _zone_path(preset_id, zone_key, "intent")
        before = self.doc["presets"][preset_id]["zones"][zone_key].get("intent", "Custom")
        op = Operation(
            patch_type="set",
            path=path,
            before=before,
            after=str(intent),
            meta=OpMeta(source="ui", reason="set_intent"),
        )
        self.doc = self.history.apply(self.doc, op)

    # -----------------
    # Geometry edits
    # -----------------
    def set_rect_px(
        self,
        preset_id: str,
        zone_key: str,
        xyxy: Tuple[int, int, int, int],
        *,
        frame_size: Optional[Tuple[int, int]] = None,
        coalesce: bool = False,
    ) -> None:
        """
        Set geometry to rect_px. Optionally clamps to frame_size (width,height).
        If coalesce=True, emits a stable coalesce_key for drag updates.
        """
        x0, y0, x1, y1 = geometry_rect.normalize_xyxy(xyxy)
        if frame_size is not None:
            w, h = frame_size
            x0, y0, x1, y1 = geometry_rect.clamp_xyxy_to_bounds((x0, y0, x1, y1), w=w, h=h)

        new_geom = {"type": "rect_px", "xyxy": [int(x0), int(y0), int(x1), int(y1)]}
        path = _zone_path(preset_id, zone_key, "geometry")
        before = self.doc["presets"][preset_id]["zones"][zone_key].get("geometry")

        op = Operation(
            patch_type="set",
            path=path,
            before=before,
            after=new_geom,
            coalesce_key=(f"geom:{preset_id}:{zone_key}" if coalesce else None),
            meta=OpMeta(source="ui", reason="set_geometry"),
        )
        self.doc = self.history.apply(self.doc, op)

    def set_rect_px_drag(
        self,
        preset_id: str,
        zone_key: str,
        xyxy: Tuple[int, int, int, int],
        *,
        frame_size: Optional[Tuple[int, int]] = None,
    ) -> None:
        """
        Coalesced rect_px update for drag operations.

        Uses the same patch path as set_rect_px while coalescing History updates.
        """
        self.set_rect_px(
            preset_id,
            zone_key,
            xyxy,
            frame_size=frame_size,
            coalesce=True,
        )

    # -----------------
    # Consumers (opaque payloads)
    # -----------------
    def set_consumer(
        self,
        preset_id: str,
        zone_key: str,
        consumer_key: str,
        payload: Optional[Dict[str, Any]],
    ) -> None:
        """
        If payload is None: remove the consumer entry.
        """
        cpath = _zone_path(preset_id, zone_key, "consumers")
        consumers = self.doc["presets"][preset_id]["zones"][zone_key].setdefault("consumers", {})
        before_all = dict(consumers)

        if payload is None:
            consumers.pop(consumer_key, None)
        else:
            consumers[str(consumer_key)] = dict(payload)

        after_all = dict(consumers)

        op = Operation(
            patch_type="set",
            path=cpath,
            before=before_all,
            after=after_all,
            meta=OpMeta(source="ui", reason="set_consumer"),
        )
        self.doc = self.history.apply(self.doc, op)
